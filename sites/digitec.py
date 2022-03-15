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
    
    def send_webhooks(self, product):
        for webhook in self.webhooks:
            self.log.sendWebhook(product, webhook)

    def load_proxies(self):
        if self.proxies != []:
            self.session = requests.Session()
            self.session.proxies = random.choice(self.proxies)
        else:
            self.session = requests.Session()



    def find_all_products(self):
        self.allCards = []
        allProducts = self.allproducts[0]["data"]["productType"]["filterProducts"]["products"]["results"]
        for product in allProducts:
            name = product["product"]["name"]
            url = "https://www.digitec.ch/product/{}".format(product["offer"]["productId"])
            try:

                picture = product["product"]["images"][0]["url"]
            except:
                picture = "https://www.digitec.ch/static/images/no-image-available.png"

            delivery = product["offer"]["deliveryOptions"]["mail"]["classification"]
            if delivery == "UNKNOWN":
                delivery = False
            else:
                delivery = True
            try:
                price = float(product["offer"]["price"]["amountIncl"])
            except:
                price = 0.0
            card = productTemplate(name, url, price, picture, self.store, delivery)

            #sendWebhook(card)
            self.allCards.append(asdict(card))
        self.log.info("Found {} products".format(len(self.allCards)))

    def getProducts(self):
        while True:
            try:
                r = self.session.post(
                url='https://www.digitec.ch/api/graphql/product-type-filter-products' + random.choice(range(10, 1000)) * "/",
                headers={
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    str(random.choice(range(11111111111,99999999999))):str(random.choice(range(11111111111,99999999999)))
                },
                json = [
                   {
                    'operationName': 'PRODUCT_TYPE_FILTER_PRODUCTS',
                    'variables': {
                        'productTypeId': int(self.product['url']),
                        'offset': 0,
                        'limit': 84,
                        'sortOrder': 'HIGHESTPRICE',
                        'siteId': None,
                        'filters': [
                            {
                                'identifier': 'off',
                                'filterType': 'TEXTUAL',
                                'options': [
                                    'Retail',
                                ],
                            },
                            {
                                'identifier': 'pr',
                                'filterType': 'NUMERICRANGE',
                                'options': [],
                                'greaterThanOrEquals': 20,
                                'lessThanOrEquals': 1000,
                            },
                        ],
                    },
                    'query': 'query PRODUCT_TYPE_FILTER_PRODUCTS($productTypeId: Int!, $filters: [SearchFilter!], $sortOrder: ProductSort, $offset: Int, $siteId: String, $limit: Int) {\n  productType(id: $productTypeId) {\n    filterProducts(\n      offset: $offset\n      limit: $limit\n      sort: $sortOrder\n      siteId: $siteId\n      filters: $filters\n    ) {\n      products {\n        hasMore\n        results {\n          ...ProductWithOffer\n          __typename\n        }\n        __typename\n      }\n      counts {\n        total\n        filteredTotal\n        __typename\n      }\n      filters {\n        identifier\n        name\n        filterType\n        score\n        tooltip {\n          ...FilterTooltipResult\n          __typename\n        }\n        ...CheckboxSearchFilterResult\n        ...RangeSearchFilterResult\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment ProductWithOffer on ProductWithOffer {\n  mandatorSpecificData {\n    ...ProductMandatorSpecific\n    __typename\n  }\n  product {\n    ...ProductMandatorIndependent\n    __typename\n  }\n  offer {\n    ...ProductOffer\n    __typename\n  }\n  __typename\n}\n\nfragment FilterTooltipResult on FilterTooltip {\n  text\n  moreInformationLink\n  __typename\n}\n\nfragment CheckboxSearchFilterResult on CheckboxSearchFilter {\n  options {\n    identifier\n    name\n    productCount\n    score\n    referenceValue {\n      value\n      unit {\n        abbreviation\n        __typename\n      }\n      __typename\n    }\n    preferredValue {\n      value\n      unit {\n        abbreviation\n        __typename\n      }\n      __typename\n    }\n    tooltip {\n      ...FilterTooltipResult\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment RangeSearchFilterResult on RangeSearchFilter {\n  referenceMin\n  preferredMin\n  referenceMax\n  preferredMax\n  referenceStepSize\n  preferredStepSize\n  rangeMergeInfo {\n    isBottomMerged\n    isTopMerged\n    __typename\n  }\n  referenceUnit {\n    abbreviation\n    __typename\n  }\n  preferredUnit {\n    abbreviation\n    __typename\n  }\n  rangeFilterDataPoint {\n    ...RangeFilterDataPointResult\n    __typename\n  }\n  __typename\n}\n\nfragment ProductMandatorSpecific on MandatorSpecificData {\n  isBestseller\n  isDeleted\n  showroomSites\n  sectorIds\n  __typename\n}\n\nfragment ProductMandatorIndependent on ProductV2 {\n  id\n  productId\n  name\n  nameProperties\n  productTypeId\n  productTypeName\n  brandId\n  brandName\n  averageRating\n  totalRatings\n  totalQuestions\n  isProductSet\n  images {\n    url\n    height\n    width\n    __typename\n  }\n  energyEfficiency {\n    energyEfficiencyColorType\n    energyEfficiencyLabelText\n    energyEfficiencyLabelSigns\n    energyEfficiencyImage {\n      url\n      height\n      width\n      __typename\n    }\n    __typename\n  }\n  seo {\n    seoProductTypeName\n    seoNameProperties\n    productGroups {\n      productGroup1\n      productGroup2\n      productGroup3\n      productGroup4\n      __typename\n    }\n    gtin\n    __typename\n  }\n  hasVariants\n  smallDimensions\n  basePrice {\n    priceFactor\n    value\n    __typename\n  }\n  __typename\n}\n\nfragment ProductOffer on OfferV2 {\n  id\n  productId\n  offerId\n  shopOfferId\n  price {\n    amountIncl\n    amountExcl\n    currency\n    fraction\n    __typename\n  }\n  deliveryOptions {\n    mail {\n      classification\n      futureReleaseDate\n      __typename\n    }\n    pickup {\n      siteId\n      classification\n      futureReleaseDate\n      __typename\n    }\n    detailsProvider {\n      productId\n      offerId\n      quantity\n      type\n      __typename\n    }\n    __typename\n  }\n  label\n  type\n  volumeDiscountPrices {\n    minAmount\n    price {\n      amountIncl\n      amountExcl\n      currency\n      __typename\n    }\n    isDefault\n    __typename\n  }\n  salesInformation {\n    numberOfItems\n    numberOfItemsSold\n    isEndingSoon\n    validFrom\n    __typename\n  }\n  incentiveText\n  isIncentiveCashback\n  isNew\n  isSalesPromotion\n  hideInProductDiscovery\n  canAddToBasket\n  hidePrice\n  insteadOfPrice {\n    type\n    price {\n      amountIncl\n      amountExcl\n      currency\n      fraction\n      __typename\n    }\n    __typename\n  }\n  minOrderQuantity\n  __typename\n}\n\nfragment RangeFilterDataPointResult on RangeFilterDataPoint {\n  count\n  referenceValue {\n    value\n    unit {\n      abbreviation\n      __typename\n    }\n    __typename\n  }\n  preferredValue {\n    value\n    unit {\n      abbreviation\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n',                },
                ]
                )
            except Exception as e:
                self.log.info(e)
                self.load_proxies()
                continue
            
            if r.status_code == 200:
                try:
                    self.allproducts = r.json()
                    self.find_all_products()
                    break
                except Exception as e:
                    self.log.info(e)
                    self.load_proxies()
                    continue
            else:
                self.load_proxies()
                self.log.info(r.status_code)
                self.log.info(r.text)
    
    def compareCards(self):
        if self.firstTime:
            self.allCardsOld = self.allCards

        differentCards = [i for i in self.allCards if i not in self.allCardsOld]
        for differentCard in differentCards:
            self.log.info(differentCard)
            if differentCard["available"]:
                self.send_webhooks(differentCard)

            else:
                self.log.info("Found Change but is bad {} {}".format(differentCard["name"],str(differentCard["available"])))
        self.allCardsOld = self.allCards


    def main(self):
        self.load_proxies()
        self.firstTime = True
        while True:
            self.getProducts()
            self.compareCards()
            time.sleep(self.product["delay"])
            self.firstTime = False

    def start(self):
        t = Thread(name=f"task-{self.__class__.__name__}-{id(self)}", target=self.main)
        t.start()