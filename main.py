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
from sites.brack import monitor as BrackMonitor
from sites.digitec import monitor as DigitecMonitor

class main():
    def __init__(self) -> None:
        pass

    
    def start(self):
        self.load_files()
        self.start_logging()
        self.start_monitors()

    def load_files(self):
        try:
            self.proxies = proxy().format_proxies(open('data/proxies.txt').read().splitlines())

            self.sites = list()
            with open('data/sites.csv') as payloads_file:
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
        ctypes.windll.kernel32.SetConsoleTitleW(f"RetailsMonitoring - {len(self.sites)} Monitors")

        for site in self.sites:

            #task changing stuf
            site['delay'] = int(float(site['delay']))
            webhooks = site['webhooks'].split(',')

            if site["site"] == "boilerplate":

                try:
                    BoilerplateMonitor(site, webhooks, self.proxies).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()


            elif site["site"] == "brack":

                try:
                    BrackMonitor(site, webhooks, self.proxies).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()

            elif site["site"] == "digitec":

                try:
                    DigitecMonitor(site, webhooks, self.proxies).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()


main().start()
