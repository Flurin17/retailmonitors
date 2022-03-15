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
                r = self.session.post(
                url=f'https://www.pc-ostschweiz.ch/de/product/list/{self.product["url"]}?sortKey=preisdesc&isFiltered=true' + random.choice(range(10, 1000)) * "/",
                headers = {
                    'authority': 'www.pc-ostschweiz.ch',
                    'content-length': '0',
                    'pragma': 'no-cache',
                    'cache-control': 'no-cache',
                    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                    'accept': '*/*',
                    'dnt': '1',
                    'x-requested-with': 'XMLHttpRequest',
                    'sec-ch-ua-mobile': '?0',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
                    'sec-ch-ua-platform': '"Windows"',
                    'origin': 'https://www.pc-ostschweiz.ch',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-dest': 'empty',
                    'referer': 'https://www.pc-ostschweiz.ch/de/product/list/spielkonsolen-stationaer-12004',
                    'accept-language': 'de-DE,de;q=0.9,en;q=0.8',
                    str(random.choice(range(11111111111,99999999999))):str(random.choice(range(11111111111,99999999999)))
                },
                allow_redirects=False
                )
            except Exception as e:
                self.log.info(e)
                continue
            
            if r.status_code == 200:
                try:
                    self.soup = r.json()
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

    def find_all_products(self):
        self.allProducts =[]
        self.soup = self.soup["newProductList"]
        self.soup = bs(self.soup, 'lxml')
        self.products = self.soup.find_all("li", {"class":"productElement product-element"})
        for product in self.products:
            url = product.find_all("a", {"class":"link-detail"})[0]["href"]
            name = product.find_all("h3")[0].text
            
            try:
                price = product.find_all("span", {"class":"price"})[0].text.replace("CHF", "").replace(" ", "")
            except:
                price = "Unknown"

            picture = product.find_all("img")[0]["src"]
            try:
                available = product.find_all("div", {"class":"productAvailability availability availability-5"})[0]['title']
                if "Lieferung morgen" in available:
                    available = True
                else:
                    available = False
            except:
                available = False

            products = productTemplate(name, url, price, picture, self.store, available)
            self.allProducts.append(asdict(products))
            print(asdict(products))
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