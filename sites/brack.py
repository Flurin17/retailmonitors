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
ctypes.windll.kernel32.SetConsoleTitleW("Brack Monitoring")



@dataclass
class Graphicscard:
    name: str
    link: str 
    price: float
    delivery: str
    picture: str
    stock: str



def log(msg):
    logmsg = "[{0}]: {1}".format(datetime.now(), msg)
    try:
        print(logmsg)
        logmsg = logmsg + "\n"
        with open ('logging.txt', 'a', newline="") as f:
            f.write(logmsg)
    except:
        print("Can't save")

def sendEveryoneWebhook():
    hook = Webhook('https://discord.com/api/webhooks/890134783252914176/C9dTbFQidjtnxxsCEDThqJrfX_CeEugkFwoWj4qC9K0lOl69zyY1p3yNJ9O_N8Q7_htg')
    hook.send("@everyone")
    log("Sent everyone webhook")

class monitor:
    def __init__(self):
        pass

    def find_all_products(self):
        self.allCards = []
        allProducts = self.allproducts.find_all("li", {"data-phptarget": "productList__item"})

        for product in allProducts:
            regex = re.compile('.*stock__amount js-stockAmount.*')
            stock = product.find_all("span", {"class": regex})[0]["data-amount"]
            name = product.find_all("span", {"class": "productList__itemTitle"})[0].text
            manufacturer =  product.find_all("span", {"class": "productList__itemManufacturer"})[0].text
            name = manufacturer + " " + name
            url = "https://www.brack.ch{}".format(product.find_all("a", {"class": "product__imageTitleLink product__imageTitleLink--title"})[0]["href"])
            picture = "https:" + product.find_all("img", {"class": "productList__itemImage js-productListImage"})[0]["data-src"]
            regex = re.compile('.*stock__amount js-stockAmount.*')
            delivery = product.find_all("span", {"class": "stock__text js-stockText"})[0].text
            try:
                price = float(product.find_all("em", {"class": "js-currentPriceValue"})[0]["content"])
            except:
                price = 0.0
            card = Graphicscard(name, url, price, delivery, picture, stock)
            self.allCards.append(asdict(card))
            log(f"{name} {price}")
  
    def sendWebhook(self):
        Graphicscard = self.differentCard
        hook = Webhook('https://discord.com/api/webhooks/890134783252914176/C9dTbFQidjtnxxsCEDThqJrfX_CeEugkFwoWj4qC9K0lOl69zyY1p3yNJ9O_N8Q7_htg')
        embed = Embed(
            description='{} for {}'.format(Graphicscard["name"], str(Graphicscard["price"])),
            color=0xe5010b,
            timestamp='now'  # sets the timestamp to current time
            )
        embed.set_author(name=Graphicscard["name"], url=Graphicscard["link"])
        embed.add_field(name='Price', value=str(Graphicscard["price"]))
        embed.add_field(name='Delivery', value=Graphicscard["delivery"])
        embed.add_field(name='Stock', value=Graphicscard["stock"])
        embed.add_field(name='IOS Retards', value=Graphicscard["link"])
        embed.set_thumbnail(Graphicscard["picture"])

        if self.stockX:
            embed.add_field(name='StockX', value="[{0}]({1})".format(self.lastSale, self.productLink))

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        embed.set_footer(text=f'BrackMoni at {dt_string}', icon_url="https://assets.brack.ch/b2c-assets/legacy/img/storeLogo.png")
        hook.send(embed=embed)

        log("Sent webhook for {}".format(Graphicscard["name"]))

    def getProducts(self):
        while True:
            try:
                r = requests.get(
                url='https://www.brack.ch/it-multimedia/pc-komponenten/grafikkarten/pc-grafikkarten?filter%5BattributeGroupFacet_grafikfamilie%5D%5B%5D=Nvidia%20GeForce%20RTX&sortProducts=newdesc&query=*',
                headers={
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    str(random.choice(range(11111111111,99999999999))):str(random.choice(range(11111111111,99999999999)))
                }
                )
            except Exception as e:
                log(e)
                continue
            
            if r.status_code == 200:
                self.allproducts = soup(r.text, 'lxml')
                self.find_all_products()
                break
            else:
                log(r.status_code)
                log(r.text)

    def getStockx(self):
        try:
            name = urllib.parse.quote_plus(self.differentCard["name"])
            log(name)
            stockSearch = "https://stockx.com/api/browse?_search={}&dataType=product".format(name)

            r = requests.get(
            url=stockSearch,
            headers = {"user-agent": "StockX/31267 CFNetwork/1206 Darwin/20.1.0 GomezAgent/3123",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-encoding": "application/json",
                "accept-language": "de-DE,de;q=0.9,en;q=0.8",
                "cache-control": "no-cache",
                "dnt": "1",
                "pragma": "no-cache",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "1",
            }
            )
        except Exception as e:
            log(e)
            self.stockX = False
            return 
        
        if r.status_code == 200:
            self.stockX = True
            try:
                websitejson = r.json()

                firstProduct = websitejson["Products"][0]
                uid = firstProduct["uuid"]
                self.productLink = "https://stockx.com/" + str(uid)
                self.lastSale = firstProduct["market"]["lastSale"]
            except:
                self.stockX = False

        else:
            log(r.status_code)
            log(r.text)

    def compareCards(self):
        if self.firstTime:
            self.allCardsOld = self.allCards

        differentCards = [i for i in self.allCards if i not in self.allCardsOld]
        log(differentCards)
        for differentCard in differentCards:
            self.differentCard = differentCard
            self.getStockx()
            self.sendWebhook()
            worth = self.checkWorth()
            if worth:
                sendEveryoneWebhook()
                self.startBot(differentCard["productId"])

        self.allCardsOld = self.allCards
        

    def checkWorth(self):
        noSpace = self.differentCard["name"].replace(" ", "").lower()

        if "3070ti" in noSpace and 750 > int(self.differentCard["price"]):
            return True

        if "3070" in noSpace and "ti" not in noSpace and 750 > int(self.differentCard["price"]):
            return True

        if "3080" in noSpace and "ti" not in noSpace and 1200 > int(self.differentCard["price"]):
            return True

        return False

    def start(self):
        self.firstTime = True
        while True:
            self.getProducts()
            self.compareCards()
            time.sleep(5)
            self.firstTime = False

monitor().start()