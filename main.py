import os
import sys
import csv
import json
import ctypes
import logging

#utils
from utils.utils import *

#monitors 
from sites.boilerplate import monitor as BoilerplateMonitor

class main():
    def __init__(self) -> None:
        pass

    def load_files(self):
        try:
            self.sites = list()
            with open('sites.csv') as payloads_file:
                reader = csv.DictReader(payloads_file)
                for row in reader:

                    self.sites.append(dict(row))

        except FileNotFoundError:
            print(">> FATAL ERROR: Could not find config file")
            input()
            sys.exit()

        except json.decoder.JSONDecodeError:
            print(">> FATAL ERROR: Could not read config file, invalid JSON")
            input()
            sys.exit()

    def start_logging(self):
        logging.basicConfig(
                level=logging.INFO,
                format="%(message)s",
                handlers=[
                    logging.StreamHandler()
                ]
            )
            
    def start_monitors(self):
        ctypes.windll.kernel32.SetConsoleTitleW(f"RetailsMonitoring - {len(self.sites)} sites")

        for site in self.sites:

            #task changing stuff
            site['delay'] = int(site['delay'])
            webhooks = site['webhooks'].split(',')

            if site["site"] == "boilerplate":

                try:
                    BoilerplateMonitor(site, webhooks).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()
