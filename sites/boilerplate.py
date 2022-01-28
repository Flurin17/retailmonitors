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
    def __init__(self, product, webhooks):
        self.product = product
        self.webhooks = webhooks

        randomString = str(random.randint(0, 10000))
        log = logger(f"{self.product['site']}_{randomString}")
        pass
    


    def main(self):
        pass

    def start(self):
        t = Thread(name=f"task-{self.__class__.__name__}-{id(self)}", target=self.main)
        t.start()