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
    
    def send_webhooks(self, link):
        for webhook in self.webhooks:
            self.log.sendBlankWebhook(webhook, link)

    def load_proxies(self):
        if self.proxies != []:
            self.session = requests.Session()
            self.session.proxies = random.choice(self.proxies)
        else:
            self.session = requests.Session()

    def getProducts(self):
        while True:
            try:
                r = self.session.get(
                url='https://www.manor.ch/de/p/' + self.product["url"],
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
                self.load_proxies()
                continue
            
            if r.status_code == 200:
                if 'Nicht verfügbar online' not in r.text:
                    self.send_webhooks(r.url)
                    break
                else:
                    self.log.info('Product is not available online')
                    time.sleep(self.product["delay"])
                    continue
            else:
                self.load_proxies()
                time.sleep(self.product["delay"])
                self.log.info(r.status_code)

    def main(self):
        self.load_proxies()
        self.getProducts()
        pass

    def start(self):
        t = Thread(name=f"task-{self.__class__.__name__}-{id(self)}", target=self.main)
        t.start()