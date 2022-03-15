import json
from dataclasses import dataclass, asdict
from threading import Thread
from winreg import HKEY_LOCAL_MACHINE
import lxml
from datetime import datetime
from dhooks import Webhook, Embed
from matplotlib.style import available
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
        self.spamLink = None
    
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
        allProducts = self.allproducts.find_all("li", {"data-phptarget": "productList__item"})

        for product in allProducts:
            regex = re.compile('.*stock__amount js-stockAmount.*')
            stock = product.find_all("span", {"class": regex})[0]["data-amount"]
            try:
                if int(stock) > 0:
                    available = True
                else:
                    available = False
            except:
                available = False
            name = product.find_all("span", {"class": "productList__itemTitle"})[0].text
            manufacturer =  product.find_all("span", {"class": "productList__itemManufacturer"})[0].text
            name = manufacturer + " " + name
            url = "https://www.brack.ch{}".format(product.find_all("a", {"class": "product__imageTitleLink product__imageTitleLink--title"})[0]["href"])
            picture = "https:" + product.find_all("img", {"class": "productList__itemImage js-productListImage"})[0]["data-src"]
            try:
                price = float(product.find_all("em", {"class": "js-currentPriceValue"})[0]["content"])
            except:
                price = 0.0
            card = productTemplate(name, url, price, picture, self.store, available)
            self.allCards.append(asdict(card))

        self.log.info("Found {} products".format(len(self.allCards)))

    def getProducts(self):
        while True:
            try:
                r = self.session.get(
                url=self.product["url"],
                headers = {
                'authority': 'www.brack.ch',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'dnt': '1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'de-DE,de;q=0.9,en;q=0.8',
                str(random.choice(range(11111111111,99999999999))):str(random.choice(range(11111111111,99999999999)))
            }
                )
            except Exception as e:
                self.log.info(e)
                continue
            
            if r.status_code == 200:
                self.allproducts = soup(r.text, 'lxml')
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
            if differentCard["link"] != self.spamLink:
                self.log.info(differentCard)
                self.send_webhooks(differentCard)
                self.spamLink = differentCard["link"]
            else:
                self.log.info("SPAM for {} on {}".format(differentCard["name"], differentCard["store"]))


        self.allCardsOld = self.allCards

    def main(self):
        self.load_proxies()
        self.firstTime = True
        while True:
            self.getProducts()
            self.find_all_products()
            self.compareCards()
            time.sleep(self.product["delay"])
            self.firstTime = False


    def start(self):
        t = Thread(name=f"task-{self.__class__.__name__}-{id(self)}", target=self.main)
        t.start()