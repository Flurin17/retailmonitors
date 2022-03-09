import json
from dataclasses import dataclass, asdict
from threading import Thread
from unicodedata import name
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

import logging

@dataclass
class productTemplate:
    name: str
    link: str 
    price: float
    picture: str
    store: str
    available: bool = False




class logger:
    def __init__(self, log_file, store, nickname):
        self.log_file = log_file
        self.store = store
        self.nickname = nickname

    def info(self, msg):
        logmsg = "[{}][{}][{}]: {}".format(datetime.now(), self.store, self.nickname, msg)
        try:
            logging.info(logmsg)
            logmsg = logmsg + "\n"
            with open (f'logs\logging_{self.log_file}.txt', 'a', newline="") as f:
                f.write(logmsg)
        except:
            print("Can't save")

    def sendEveryoneWebhook(self, webhook):
        hook = Webhook(webhook)
        try:
            hook.send("@everyone")
        except:
            self.info("Can't send webhook")

        self.info("Sent everyone webhook")


    def sendWebhook(self, product, webhook):
        hook = Webhook(webhook, avatar_url="https://cdn.discordapp.com/attachments/637694919871430657/936708268317868033/celar-logo-small.png", username=product["store"])
        embed = Embed(
            description='{} for {}'.format(product["name"], str(product["price"])),
            color=0x00559d,
            timestamp='now'  # sets the timestamp to current time
            )
        embed.set_author(name=product["name"], url=product["link"])
        embed.add_field(name='Price', value=str(product["price"]))
        embed.add_field(name='Links', value=product["link"])
        embed.add_field(name='Delivery', value=product["available"])
        embed.set_thumbnail(product["picture"])


        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        embed.set_footer(text=f'{product["store"]} at {dt_string}', icon_url="https://cdn.discordapp.com/attachments/637694919871430657/936708268317868033/celar-logo-small.png")
        try:
            hook.send(embed=embed)
        except:
            self.info("Can't send webhook")

        self.info("Sent webhook for {} on {}".format(product["name"], product["store"]))
    
    def sendBlankWebhook(self, webhook, link):
        hook = Webhook(webhook, avatar_url="https://cdn.discordapp.com/attachments/637694919871430657/936708268317868033/celar-logo-small.png")
        embed = Embed(
            description='New Product',
            color=0x00559d,
            timestamp='now'  # sets the timestamp to current time
            )
        embed.add_field(name='Links', value=link)


        try:
            hook.send(embed=embed)
        except:
            self.info("Can't send webhook")

    def sendMonitorFailed(self, webhook, amountRunning):
        hook = Webhook(webhook, avatar_url="https://cdn.discordapp.com/attachments/637694919871430657/936708268317868033/celar-logo-small.png")
        embed = Embed(
            description='Monitor failed please check',
            color=0x00559d,
            timestamp='now'  # sets the timestamp to current time
            )
        embed.add_field(name='Running monitors', value=amountRunning)


        try:
            hook.send(embed=embed)
        except:
            self.info("Can't send webhook")


class proxy:
    def __init__(self):
        self.proxyList = []

    def format_proxies(self, proxies):
        for proxy in proxies:
            try:
                ip = proxy.split(":")[0]
                port = proxy.split(":")[1]
                userpassproxy = '%s:%s' % (ip, port)
                proxyuser = proxy.split(":")[2].rstrip()
                proxypass = proxy.split(":")[3].rstrip()
                parsedProxy = {'http': 'http://%s:%s@%s' % (proxyuser, proxypass, userpassproxy),
                        'https': 'http://%s:%s@%s' % (proxyuser, proxypass, userpassproxy)}
                self.proxyList.append(parsedProxy)
            except:
                parsedProxy = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy}
                self.proxyList.append(parsedProxy)
                
        return self.proxyList