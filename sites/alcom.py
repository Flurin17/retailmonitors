import json
from dataclasses import dataclass, asdict
from threading import Thread
import lxml
from datetime import datetime
from dhooks import Webhook, Embed
import requests
import time
import pymongo
import random
import urllib.parse
import re
from bs4 import BeautifulSoup as soup
import ctypes
import urllib.parse

from utils.utils import *

class monitor:
    def __init__(self, product, webhooks, proxies):
        self.product = product
        self.webhooks = webhooks
        self.proxies = proxies

        self.productUrlEncoded = urllib.parse.quote(self.product["url"])
        self.store = product["site"]
        randomString = str(random.randint(0, 10000))
        self.log = logger(f"{self.product['site']}_{randomString}", self.store, self.product["nickname"])


        pass
    
    def send_webhooks(self, product):
        for webhook in self.webhooks:
            self.log.sendWebhook(product, webhook)

    def load_proxies(self):
        if self.proxies != []:
            self.session = requests.Session()
            self.session.proxies = random.choice(self.proxies)
        else:
            self.session = requests.Session()



    def find_all_products(self):
        self.allCards = []
        allProducts = self.allproducts['geonames']
        for product in allProducts:
            name = product["name"]
            nameUrlEncoded = urllib.parse.quote(name)
            url = f"https://www.alcom.ch/index.php?suchtext={nameUrlEncoded}&hm=suche"
            picture = "https://www.alcom.ch/bilder/logo_alcom_200h.jpg"

            delivery = True
            price = 0.0

            card = productTemplate(name, url, price, picture, self.store, delivery)
            self.allCards.append(asdict(card))
        self.log.info("Found {} products".format(len(self.allCards)))

    def getProducts(self):
        while True:
            try:
                r = self.session.get(
                url=f"https://www.alcom.ch/search.php?featureClass=P&style=full&maxRows=50&name_startsWith=" + self.productUrlEncoded,
                headers = {
                    'Connection': 'keep-alive',
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache',
                    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'DNT': '1',
                    'X-Requested-With': 'XMLHttpRequest',
                    'sec-ch-ua-mobile': '?0',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.69',
                    'sec-ch-ua-platform': '"Windows"',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Referer': 'https://www.alcom.ch/',
                    'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
                }
                )
            except Exception as e:
                self.log.info(e)
                self.load_proxies()
                continue
            
            if r.status_code == 200:
                try:
                    self.allproducts = r.json()
                    self.find_all_products()
                    break
                except Exception as e:
                    self.log.info(e)
                    self.load_proxies()
                    continue
            else:
                self.load_proxies()
                self.log.info(r.status_code)
                self.log.info(r.text)
    
    def compareCards(self):
        if self.firstTime:
            self.allCardsOld = self.allCards

        differentCards = [i for i in self.allCards if i not in self.allCardsOld]
        for differentCard in differentCards:
            self.log.info(differentCard)
            if differentCard["available"]:
                self.send_webhooks(differentCard)

            else:
                self.log.info("Found Change but is bad {} {}".format(differentCard["name"],str(differentCard["available"])))
        self.allCardsOld = self.allCards


    def main(self):
        self.load_proxies()
        self.firstTime = True
        while True:
            self.getProducts()
            self.compareCards()
            time.sleep(self.product["delay"])
            self.firstTime = False

    def start(self):
        t = Thread(name=f"task-{self.__class__.__name__}-{id(self)}", target=self.main)
        t.start()