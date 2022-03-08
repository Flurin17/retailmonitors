import json
from dataclasses import dataclass, asdict
from threading import Thread
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
from bs4 import BeautifulSoup as bs
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

    def get_all_products(self):
        while True:
            try:
                r = self.session.get(
                url=self.product["url"],
                headers={
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    str(random.choice(range(11111111111,99999999999))):str(random.choice(range(11111111111,99999999999)))
                },
                allow_redirects=False
                )
            except Exception as e:
                self.log.info(e)
                continue
            
            if r.status_code == 200:
                self.soup = bs(r.text, 'lxml')
                break
            else:
                self.load_proxies()
                self.log.info(r.status_code)
                self.log.info(r.text)

    def find_all_products(self):
        self.allProducts =[]
        self.products = self.soup.find_all("div", {"class":"product-wrapper"})
        for product in self.products:
            url = "https://www.mediamarkt.ch" + product.find_all("span", {"class":"photo clickable"})[0]['data-clickable-href']
            name = product.find_all("img")[0]['alt']
            
            price = "Unknown"

            picture = "https:" + product.find_all("img")[0]['src']
            try:
                available = product.find_all("font")[0]['color']
            except:
                try:
                    available = product.find_all("p")[0]['style']
                except:
                    available = "green"

            if 'green' in available:
                available = True
            else:
                available = False

            products = productTemplate(name, url, price, picture, self.store, available)
            self.allProducts.append(asdict(products))
        self.log.info("Found {} products".format(len(self.allProducts)))

    def compare_Products(self):
        if self.firstTime:
            self.allProductsOld = self.allProducts

        differentProducts = [i for i in self.allProducts if i not in self.allProductsOld]
        for differentProduct in differentProducts:
            self.log.info(differentProduct)
            self.send_webhooks(differentProduct)

        self.allProductsOld = self.allProducts

    def main(self):
        self.firstTime = True
        while True:
            self.load_proxies()
            self.get_all_products()
            self.find_all_products()
            self.compare_Products()
            time.sleep(self.product["delay"])
            self.firstTime = False
        

    def start(self):
        t = Thread(name=f"task-{self.__class__.__name__}-{id(self)}", target=self.main)
        t.start()