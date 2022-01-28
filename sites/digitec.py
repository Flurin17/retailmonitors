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



        self.productType = int(product['url'].split(",")[0])
        self.filter = product['url'].split(",")[1]
        pass
    
    def send_webhooks(self):
        for webhook in self.webhooks:
            self.log.sendWebhook(self.product, webhook)

    def load_proxies(self):
        if self.proxies != []:
            self.session = requests.Session()
            self.session.proxies = random.choice(self.proxies)
        else:
            self.session = requests.Session()



    def find_all_products(self):
        self.allCards = []
        allProducts = self.allproducts[0]["data"]["productType"]["filterProductsV4"]["products"]["resultsWithDefaultOffer"]

        for product in allProducts:
            productId = product["product"]["productId"]
            name = product["product"]["name"]
            url = "https://www.digitec.ch/product/{}".format(product["offer"]["productId"])
            picture = product["product"]["images"][0]["url"]
            delivery = product["offer"]["deliveryOptions"]["mail"]["classification"]
            try:
                price = float(product["offer"]["price"]["amountIncl"])
            except:
                price = 0.0
            card = productTemplate(name, url, price, picture, self.store)
            #sendWebhook(card)
            self.allCards.append(asdict(card))
        self.log.info("Found {} products".format(len(self.allCards)))

    def getProducts(self):
        while True:
            try:
                r = self.session.post(
                url='https://www.digitec.ch/api/graphql',
                headers={
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    str(random.choice(range(11111111111,99999999999))):str(random.choice(range(11111111111,99999999999)))
                },
                json=[{"operationName":"GET_PRODUCT_TYPE_PRODUCTS_AND_FILTERS","variables":{"productTypeId":self.productType,"queryString": self.filter,"offset":0,"limit":100,"sort":"BESTSELLER","siteId":"0","sectorId":1},"query":"query GET_PRODUCT_TYPE_PRODUCTS_AND_FILTERS($productTypeId: Int!, $queryString: String!, $offset: Int, $limit: Int, $sort: ProductSort, $siteId: String, $sectorId: Int) {  productType(id: $productTypeId) {    filterProductsV4(queryString: $queryString, offset: $offset, limit: $limit, sort: $sort, siteId: $siteId, sectorId: $sectorId) {      productCounts {        total        filteredTotal        __typename      }      productFilters {        filterGroupType        label        key        tooltip {          ...Tooltip          __typename        }        ...CheckboxFilterGroup        ...RangeSliderFilterGroup        __typename      }      products {        hasMore        resultsWithDefaultOffer {          ...ProductWithOffer          __typename        }        __typename      }      __typename    }    __typename  }}fragment Tooltip on Tooltip {  text  moreInformationLink  __typename}fragment CheckboxFilterGroup on CheckboxFilterGroupV2 {  filterOptions {    ...Filter    __typename  }  __typename}fragment RangeSliderFilterGroup on RangeSliderFilterGroupV2 {  dataPoints {    ...RangeSliderDataPoint    __typename  }  selectedRange {    min    max    __typename  }  optionIdentifierKey  unitAbbreviation  unitDisplayOrder  totalCount  fullRange {    min    max    __typename  }  stepSize  mergeInfo {    isBottomMerged    isTopMerged    __typename  }  __typename}fragment ProductWithOffer on ProductWithOffer {  mandatorSpecificData {    ...ProductMandatorSpecific    __typename  }  product {    ...ProductMandatorIndependent    __typename  }  offer {    ...ProductOffer    __typename  }  __typename}fragment Filter on Filter {  optionIdentifierKey  optionIdentifierValue  label  productCount  selected  tooltip {    ...Tooltip    __typename  }  __typename}fragment RangeSliderDataPoint on RangeSliderDataPoint {  value  productCount  __typename}fragment ProductMandatorSpecific on MandatorSpecificData {  isBestseller  isDeleted  showroomSites  sectorIds  __typename}fragment ProductMandatorIndependent on ProductV2 {  id  productId  name  nameProperties  productTypeId  productTypeName  brandId  brandName  averageRating  totalRatings  totalQuestions  isProductSet  images {    url    height    width    __typename  }  energyEfficiency {    energyEfficiencyColorType    energyEfficiencyLabelText    energyEfficiencyLabelSigns    energyEfficiencyImage {      url      height      width      __typename    }    __typename  }  seo {    seoProductTypeName    seoNameProperties    productGroups {      productGroup1      productGroup2      productGroup3      productGroup4      __typename    }    gtin    __typename  }  lowQualityImagePlaceholder  hasVariants  smallDimensions  basePrice {    priceFactor    value    __typename  }  __typename}fragment ProductOffer on OfferV2 {  id  productId  offerId  shopOfferId  price {    amountIncl    amountExcl    currency    fraction    __typename  }  deliveryOptions {    mail {      classification      futureReleaseDate      __typename    }    pickup {      siteId      classification      futureReleaseDate      __typename    }    detailsProvider {      productId      offerId      quantity      type      __typename    }    __typename  }  label  type  volumeDiscountPrices {    minAmount    price {      amountIncl      amountExcl      currency      __typename    }    isDefault    __typename  }  salesInformation {    numberOfItems    numberOfItemsSold    isEndingSoon    validFrom    __typename  }  incentiveText  isIncentiveCashback  isNew  isSalesPromotion  hideInProductDiscovery  canAddToBasket  hidePrice  insteadOfPrice {    type    price {      amountIncl      amountExcl      currency      fraction      __typename    }    __typename  }  minOrderQuantity  __typename}"}]
                )
            except Exception as e:
                self.log.info(e)
                self.load_proxies()
                continue
            
            if r.status_code == 200:
                self.allproducts = r.json()
                self.find_all_products()
                break
            else:
                self.load_proxies()
                self.log.info(r.status_code)
                self.log.info(r.text)
    
    def compareCards(self):
        if self.firstTime:
            self.allCardsOld = self.allCards

        differentCards = [i for i in self.allCards if i not in self.allCardsOld]
        self.log.info(differentCards)
        for differentCard in differentCards:
            if differentCard["delivery"] not in ["UNKNOWN", "LAUNCH"]:
                self.send_webhooks(differentCard)

            else:
                self.log.info("Found Change but is bad {} {}".format(differentCard["name"],differentCard["delivery"]))
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