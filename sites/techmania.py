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
            url = product["url"]
            picture = product["image"]
            
            price = "Unknown"
            delivery = True

            card = productTemplate(name, url, price, picture, self.store, delivery)

            #sendWebhook(card)
            self.allCards.append(asdict(card))
        self.log.info("Found {} products".format(len(self.allCards)))

    def compareProducts(self):
        if self.firstTime:
            self.allCardsOld = self.allCards

        differentCards = [i for i in self.allCards if i not in self.allCardsOld]
        for differentCard in differentCards:
            self.log.info(differentCard)
            self.send_webhooks(differentCard)

        self.allCardsOld = self.allCards

    def getProducts(self):
            while True:
                try:
                    r = self.session.post(
                    url='https://77.58.177.73/de/Lightweight/GetSuggestions',
                    headers={
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                        'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        str(random.choice(range(11111111111,99999999999))):str(random.choice(range(11111111111,99999999999))),
                        'Host': 'www.techmania.ch'
                    },
                    json = {
                        'suche': self.product["url"],
                        'languageId': 'de',
                        'host': 'https://www.techmania.ch'
                    },
                    verify=False
                    )
                except Exception as e:
                    self.log.info(e)
                    self.load_proxies()
                    continue
                
                if r.status_code == 200:
                    self.allproducts = r.json()
                    break
                else:
                    self.load_proxies()
                    self.log.info(r.status_code)
                    self.log.info(r.text)

    def main(self):
        self.load_proxies()
        self.firstTime = True
        while True:
            self.getProducts()
            self.find_all_products()
            self.compareProducts()
            time.sleep(self.product["delay"])
            self.firstTime = False


    def start(self):
        t = Thread(name=f"task-{self.__class__.__name__}-{id(self)}", target=self.main)
        t.start()