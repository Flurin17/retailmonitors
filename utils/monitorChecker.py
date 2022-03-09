import json
from dataclasses import dataclass, asdict
from threading import Thread
import threading
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

from utils.utils import *

class monitor:
    def __init__(self, webhooks, amountMonitors):
        self.webhooks = webhooks
        self.amountMonitors = amountMonitors

        randomString = str(random.randint(0, 10000))
        self.log = logger(f"Monitor_{randomString}", "Monitor", 'MonitorChecker')
        pass
    
    def send_webhooks(self, amountStillRunning):
        for webhook in self.webhooks:
            self.log.sendMonitorFailed(webhook, amountStillRunning)



    def main(self):
        time.sleep(5)
        while True:
            runningMonitors = threading.active_count()
            amountStillRunning = f"{runningMonitors}/{self.amountMonitors}"
            
            if runningMonitors == self.amountMonitors:
                self.log.info(amountStillRunning)
                time.sleep(5)
                continue
            else:
                self.log.info(amountStillRunning)
                self.send_webhooks(amountStillRunning)

                # set down amount of actual monitors to avoid spam
                self.amountMonitors = runningMonitors
                continue



    def start(self):
        t = Thread(name=f"task-{self.__class__.__name__}-{id(self)}", target=self.main)
        t.start()