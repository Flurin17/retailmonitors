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

import ssl
import cloudscraper
from utils.cloudflaresolving.hawk_cf import CF_2,Cf_challenge_3
import re

# ------------------------------------------------------------------------------ cloudscraper is not passing proxies to the requests module, thus we need to monkey
def perform_request(self, method, url, *args, **kwargs):
    if "proxies" in kwargs or "proxy"  in kwargs:
        return super(cloudscraper.CloudScraper, self).request(method, url, *args, **kwargs)
    else:
        return super(cloudscraper.CloudScraper, self).request(method, url, *args, **kwargs,proxies=self.proxies)
# monkey patch the method in
cloudscraper.CloudScraper.perform_request = perform_request
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------ SNS updated theire challenge strings leading to defualt cloudscraper regex not matching anymore thus monkey these as well
#cap challenge
@staticmethod
def is_New_Captcha_Challenge(resp):
    try:
        return (
                resp.headers.get('Server', '').startswith('cloudflare')
                and resp.status_code == 403
                and re.search(
                    r'cpo.src\s*=\s*"/cdn-cgi/challenge-platform/?\w?/?\w?/orchestrate/.*/v1',
                    resp.text,
                    re.M | re.S
                )
                and re.search(r'window._cf_chl_opt', resp.text, re.M | re.S)
        )
    except AttributeError:
        pass

    return False
cloudscraper.CloudScraper.is_New_Captcha_Challenge = is_New_Captcha_Challenge

#normal challenge
@staticmethod
def is_New_IUAM_Challenge(resp):
    try:
        return (
                resp.headers.get('Server', '').startswith('cloudflare')
                and resp.status_code in [429, 503]
                and re.search(
                    r'cpo.src\s*=\s*"/cdn-cgi/challenge-platform/?\w?/?\w?/orchestrate/jsch/v1',
                    resp.text,
                    re.M | re.S
                )
                and re.search(r'window._cf_chl_opt', resp.text, re.M | re.S)
        )
    except AttributeError:
        pass

    return False
cloudscraper.CloudScraper.is_New_IUAM_Challenge = is_New_IUAM_Challenge

## fingerprint challenge
def is_fingerprint_challenge(resp):
    try:
        if resp.status_code == 429:
            if "/fingerprint/script/" in resp.text:
                return True
        return False
    except:
        pass

# injection of our api
# ------------------------------------------------------------------------------- #
api_key = "test_1fdcce24-5733-42a2-8313-04e590cd3393"
if not api_key:
    raise Exception("Api Key must be given")
def injection(session, response):
    if session.is_New_IUAM_Challenge(response):
        return CF_2(session,response,key=api_key,captcha=False,debug=True).solve() # FALSE is actually the default value but is displayed here to show that you need to have it true for captcha handling
                                                    # note that currently no captcha token getter is provided you can edit the file and add your solution
    elif session.is_New_Captcha_Challenge(response):
        return CF_2(session, response, key=api_key, captcha=True,
                    debug=True).solve()
    elif is_fingerprint_challenge(response):
        return Cf_challenge_3(session,response,key=api_key,debug=True).solve()



    else:
        return response

# ------------------------------------------------------------------------------- #

ssl_context = ssl.create_default_context()
ssl_context.set_ciphers('ECDH-RSA-NULL-SHA:ECDH-RSA-RC4-SHA:ECDH-RSA-DES-CBC3-SHA:ECDH-RSA-AES128-SHA:ECDH-RSA-AES256-SHA:ECDH-ECDSA-NULL-SHA:ECDH-ECDSA-RC4-SHA:ECDH-ECDSA-DES-CBC3-SHA:ECDH-ECDSA-AES128-SHA:ECDH-ECDSA-AES256-SHA:ECDHE-RSA-NULL-SHA:ECDHE-RSA-RC4-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-NULL-SHA:ECDHE-ECDSA-RC4-SHA:ECDHE-ECDSA-DES-CBC3-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:AECDH-NULL-SHA:AECDH-RC4-SHA:AECDH-DES-CBC3-SHA:AECDH-AES128-SHA:AECDH-AES256-SHA')
ssl_context.set_ecdh_curve('prime256v1')
ssl_context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1_3 | ssl.OP_NO_TLSv1)
ssl_context.check_hostname=False

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
            self.session = cloudscraper.create_scraper(
            browser={
                'custom': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
                #'platform': 'darwin'
            },captcha={'provider':'2captcha','api_key':"f3f000c19a1e0d44001c90c5c8f820e7", 'no_proxy':True},
            doubleDown=False,
            requestPostHook=injection,
            debug=False,
            ssl_context = ssl_context
        )
            self.session.proxies = random.choice(self.proxies)
        else:
            self.session = cloudscraper.create_scraper(
            browser={
                'custom': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
                #'platform': 'darwin'
            },captcha={'provider':'2captcha','api_key':"f3f000c19a1e0d44001c90c5c8f820e7", 'no_proxy':True},
            doubleDown=False,
            requestPostHook=injection,
            debug=False,
            ssl_context = ssl_context
        )

    def get_all_products(self):
        while True:
            try:
                r = self.session.post(
                url=f'https://www.pc-ostschweiz.ch/de/product/list/{self.product["url"]}?sortKey=preisdesc&isFiltered=true'
                )
            except Exception as e:
                self.log.info(e)
                continue
            
            if r.status_code == 200:
                try:
                    self.jsonResponse = r.json()
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
        self.soup = self.jsonResponse["newProductList"]
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
        self.load_proxies()
        while True:
            self.get_all_products()
            self.find_all_products()
            self.compare_Products()
            time.sleep(self.product["delay"])
            self.firstTime = False
        

    def start(self):
        t = Thread(name=f"task-{self.__class__.__name__}-{id(self)}", target=self.main)
        t.start()