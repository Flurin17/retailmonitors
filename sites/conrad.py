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
        allProducts = self.allproducts['hits']
        for product in allProducts:
            name = product["title"]
            url = "https://www.conrad.ch/de/p/{}.html".format(product["productId"])
            try:
                picture = product["image"]
            except:
                picture = "https://www.digitec.ch/static/images/no-image-available.png"

            delivery = product["isBuyable"]

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
                headers = {
                    'Connection': 'keep-alive',
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache',
                    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                    'DNT': '1',
                    'Conrad-PageAction-Id': '697c5230-1daa-4aa1-a490-ad36595e10fb',
                    'Conrad-Session-Id': 'a9f85d87-35d6-49a6-bf18-79d27a3bad79',
                    'sec-ch-ua-mobile': '?0',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
                    'Accept': 'application/json, text/plain, */*',
                    'sec-ch-ua-platform': '"Windows"',
                    'Origin': 'https://www.conrad.ch',
                    'Sec-Fetch-Site': 'same-site',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Referer': 'https://www.conrad.ch/',
                    'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
                }

                params = (
                    ('apikey', '2cHbdksbmXc6PQDkPzRVFOcdladLvH7w'),
                )

                json_data = {
                    'query': '',
                    'enabledFeatures': [
                        'and_filters',
                        'filters_without_values',
                        'query_relaxation',
                    ],
                    'disabledFeatures': [],
                    'globalFilter': [
                        {
                            'field': 'categoryId',
                            'type': 'TERM_OR',
                            'value': self.product['url'],
                        },
                    ],
                    'facetFilter': [
                        {
                            'field': 'brand',
                            'type': 'TERM_OR',
                            'values': [
                                'Sony',
                            ],
                        },
                        {
                            'field': 'availabilityColor',
                            'type': 'TERM_OR',
                            'values': [
                                'green',
                            ],
                        },
                    ],
                    'sort': [
                        {
                            'field': 'price',
                            'order': 'desc',
                        },
                    ],
                    'from': 0,
                    'size': 30,
                    'facets': [],
                    'partialThreshold': 10,
                    'partialQueries': 3,
                    'partialQuerySize': 6,
                }

                r = self.session.post('https://api.conrad.ch/search/1/v3/facetSearch/ch/de/b2c', headers=headers, params=params, json=json_data)
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