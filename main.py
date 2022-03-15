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
from sites.manor import monitor as ManorMonitor
from sites.wog import monitor as WogMonitor
from sites.preispirat import monitor as PreispiratMonitor
from sites.steg import monitor as StegMonitor
from sites.techmania import monitor as TechmaniaMonitor
from sites.softridge import monitor as SoftridgeMonitor
from sites.mediamarkt import monitor as MediamarktMonitor
from sites.melectronics import monitor as MelectronicsMonitor
from sites.conrad import monitor as ConradMonitor
from sites.alcom import monitor as AlcomMonitor
from sites.pcostschweiz import monitor as PcostschweizMonitor

from utils.monitorChecker import monitor as MonitorChecker
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
        amountRunning = len(self.sites) + 1
        for site in self.sites:

            #task changing stuff
            try:
                site['delay'] = int(float(site['delay']))
                webhooks = site['webhooks'].split(',')
            except:
                print(f">> FATAL ERROR: Could not parse site {site['site']}")
                break

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

            elif site["site"] == "manor":
                try:
                    ManorMonitor(site, webhooks, self.proxies).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()
                
            elif site["site"] == "wog":
                try:
                    WogMonitor(site, webhooks, self.proxies).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()

            elif site["site"] == "preispirat":
                try:
                    PreispiratMonitor(site, webhooks, self.proxies).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()

            elif site["site"] == "steg":
                try:
                    StegMonitor(site, webhooks, self.proxies).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()

            elif site["site"] == "techmania":
                try:
                    TechmaniaMonitor(site, webhooks, self.proxies).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()

            elif site["site"] == "softridge":
                try:
                    SoftridgeMonitor(site, webhooks, self.proxies).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()
                    
            elif site["site"] == "mediamarkt":
                try:
                    MediamarktMonitor(site, webhooks, self.proxies).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()

            elif site["site"] == "melectronics":
                try:
                    MelectronicsMonitor(site, webhooks, self.proxies).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()

            elif site["site"] == "conrad":
                try:
                    ConradMonitor(site, webhooks, self.proxies).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()

            elif site["site"] == "alcom":
                try:
                    AlcomMonitor(site, webhooks, self.proxies).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()

            elif site["site"] == "pcostschweiz":
                try:
                    PcostschweizMonitor(site, webhooks, self.proxies).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()



            #special monitors
            elif site["site"] == "monitorchecker":
                try:
                    MonitorChecker(webhooks, amountRunning).start()

                except Exception as e:
                    print(f">> FATAL ERROR: Could not start monitor {e}")
                    sys.exit()

main().start()
