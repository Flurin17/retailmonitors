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

import logging

class logger:
    def __init__(self, log_file):
        self.log_file = log_file

    def log(self, msg):
        logmsg = "[{0}]: {1}".format(datetime.now(), msg)
        try:
            logging.info(logmsg)
            logmsg = logmsg + "\n"
            with open (f'logs\logging_{self.log_file}.txt', 'a', newline="") as f:
                f.write(logmsg)
        except:
            print("Can't save")

    def sendEveryoneWebhook(self, webhook):
        hook = Webhook(webhook)
        hook.send("@everyone")
        self.log("Sent everyone webhook")


    def sendWebhook(self, product, webhook):
        hook = Webhook(webhook)
        embed = Embed(
            description='{} for {}'.format(product["name"], str(product["price"])),
            color=0x00559d,
            timestamp='now'  # sets the timestamp to current time
            )
        embed.set_author(name=product["name"], url=product["link"])
        embed.add_field(name='Price', value=str(product["price"]))
        embed.add_field(name='delivery', value=product["delivery"])
        embed.add_field(name='Links', value=product["link"])
        embed.set_thumbnail(product["picture"])


        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        embed.set_footer(text=f'{product["store"]} at {dt_string}', icon_url="https://cdn.discordapp.com/attachments/637694919871430657/936708268317868033/celar-logo-small.png")
        hook.send(embed=embed)

        self.log("Sent webhook for {}".format(product["name"]))