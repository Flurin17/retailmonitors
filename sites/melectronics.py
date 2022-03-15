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


from utils.utils import *

class monitor:
    def __init__(self, product, webhooks, proxies):
        self.product = product
        self.webhooks = webhooks
        self.proxies = proxies

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
        allProducts = self.allproducts['products']
        for product in allProducts:
            name = product["name"]
            url = "https://www.melectronics.ch{}".format(product["url"])
            try:
                picture = product["images"][0]["url"].replace('{stack}', "fm-sm")
            except:
                picture = "https://www.digitec.ch/static/images/no-image-available.png"

            delivery = product["orderable"]
            try:
                price = float(product["price"]["value"])
            except:
                price = 0.0
            card = productTemplate(name, url, price, picture, self.store, delivery)
            self.allCards.append(asdict(card))
        self.log.info("Found {} products".format(len(self.allCards)))

    def getProducts(self):
        while True:
            try:
                r = self.session.get(
                url=f"https://www.melectronics.ch/jsapi/v1/de/products/search?q={self.product['url']}&pageSize=69&currentPage=0",
                headers = {
                    'Connection': 'keep-alive',
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache',
                    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'DNT': '1',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                    'Accept-Language': 'de-DE,de;q=0.9',
                }
                )
            except Exception as e:
                self.log.info(e)
                self.load_proxies()
                continue
            
            if r.status_code == 200:
                self.allproducts = r.json()
                self.find_all_products()
                break
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