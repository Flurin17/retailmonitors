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

import ctypes
ctypes.windll.kernel32.SetConsoleTitleW("Digitec Monitoring")



@dataclass
class Graphicscard:
    productId: int
    name: str
    link: str 
    price: float
    delivery: str
    picture: str



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
    hook = Webhook('https://discord.com/api/webhooks/884699851844112425/qxFB0dQnKlQ5Iidq_6b4L_cnXt4teXpGOdsNRrQmXXeP75VDYKbUvzn_skOZ7SUmFEfU')
    hook.send("@everyone")
    log("Sent everyone webhook")

class monitor:
    def __init__(self):
        pass

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
            
            card = Graphicscard(productId, name, url, price, delivery, picture)
            #sendWebhook(card)
            self.allCards.append(asdict(card))
            log(f"{name} {price}")
  
    def sendWebhook(self):
        Graphicscard = self.differentCard
        hook = Webhook('https://discord.com/api/webhooks/884699851844112425/qxFB0dQnKlQ5Iidq_6b4L_cnXt4teXpGOdsNRrQmXXeP75VDYKbUvzn_skOZ7SUmFEfU')
        embed = Embed(
            description='{} for {}'.format(Graphicscard["name"], str(Graphicscard["price"])),
            color=0x00559d,
            timestamp='now'  # sets the timestamp to current time
            )
        embed.set_author(name=Graphicscard["name"], url=Graphicscard["link"])
        embed.add_field(name='Price', value=str(Graphicscard["price"]))
        embed.add_field(name='delivery', value=Graphicscard["delivery"])
        embed.add_field(name='IOS Retards', value=Graphicscard["link"])
        embed.set_thumbnail(Graphicscard["picture"])

        if self.stockX:
            embed.add_field(name='StockX', value="[{0}]({1})".format(self.lastSale, self.productLink))

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        embed.set_footer(text=f'DigitecMoni at {dt_string}', icon_url="https://www.digitec.ch/static/images/digitec/pwa/favicon-32x32.png?v=2")
        hook.send(embed=embed)

        log("Sent webhook for {}".format(Graphicscard["name"]))

    def getProducts(self):
        while True:
            try:
                r = requests.post(
                url='https://www.digitec.ch/api/graphql',
                headers={
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    str(random.choice(range(11111111111,99999999999))):str(random.choice(range(11111111111,99999999999)))
                },
                json=[{"operationName":"GET_PRODUCT_TYPE_PRODUCTS_AND_FILTERS","variables":{"productTypeId":106,"queryString":"price=56.9%3A3000&oo=1&pdo=39-666%3A742%7C389-16726%3A491245","offset":0,"limit":100,"sort":"AVAILABILITY","siteId":"0","sectorId":1},"query":"query GET_PRODUCT_TYPE_PRODUCTS_AND_FILTERS($productTypeId: Int!, $queryString: String!, $offset: Int, $limit: Int, $sort: ProductSort, $siteId: String, $sectorId: Int) {  productType(id: $productTypeId) {    filterProductsV4(queryString: $queryString, offset: $offset, limit: $limit, sort: $sort, siteId: $siteId, sectorId: $sectorId) {      productCounts {        total        filteredTotal        __typename      }      productFilters {        filterGroupType        label        key        tooltip {          ...Tooltip          __typename        }        ...CheckboxFilterGroup        ...RangeSliderFilterGroup        __typename      }      products {        hasMore        resultsWithDefaultOffer {          ...ProductWithOffer          __typename        }        __typename      }      __typename    }    __typename  }}fragment Tooltip on Tooltip {  text  moreInformationLink  __typename}fragment CheckboxFilterGroup on CheckboxFilterGroupV2 {  filterOptions {    ...Filter    __typename  }  __typename}fragment RangeSliderFilterGroup on RangeSliderFilterGroupV2 {  dataPoints {    ...RangeSliderDataPoint    __typename  }  selectedRange {    min    max    __typename  }  optionIdentifierKey  unitAbbreviation  unitDisplayOrder  totalCount  fullRange {    min    max    __typename  }  stepSize  mergeInfo {    isBottomMerged    isTopMerged    __typename  }  __typename}fragment ProductWithOffer on ProductWithOffer {  mandatorSpecificData {    ...ProductMandatorSpecific    __typename  }  product {    ...ProductMandatorIndependent    __typename  }  offer {    ...ProductOffer    __typename  }  __typename}fragment Filter on Filter {  optionIdentifierKey  optionIdentifierValue  label  productCount  selected  tooltip {    ...Tooltip    __typename  }  __typename}fragment RangeSliderDataPoint on RangeSliderDataPoint {  value  productCount  __typename}fragment ProductMandatorSpecific on MandatorSpecificData {  isBestseller  isDeleted  showroomSites  sectorIds  __typename}fragment ProductMandatorIndependent on ProductV2 {  id  productId  name  nameProperties  productTypeId  productTypeName  brandId  brandName  averageRating  totalRatings  totalQuestions  isProductSet  images {    url    height    width    __typename  }  energyEfficiency {    energyEfficiencyColorType    energyEfficiencyLabelText    energyEfficiencyLabelSigns    energyEfficiencyImage {      url      height      width      __typename    }    __typename  }  seo {    seoProductTypeName    seoNameProperties    productGroups {      productGroup1      productGroup2      productGroup3      productGroup4      __typename    }    gtin    __typename  }  lowQualityImagePlaceholder  hasVariants  smallDimensions  basePrice {    priceFactor    value    __typename  }  __typename}fragment ProductOffer on OfferV2 {  id  productId  offerId  shopOfferId  price {    amountIncl    amountExcl    currency    fraction    __typename  }  deliveryOptions {    mail {      classification      futureReleaseDate      __typename    }    pickup {      siteId      classification      futureReleaseDate      __typename    }    detailsProvider {      productId      offerId      quantity      type      __typename    }    __typename  }  label  type  volumeDiscountPrices {    minAmount    price {      amountIncl      amountExcl      currency      __typename    }    isDefault    __typename  }  salesInformation {    numberOfItems    numberOfItemsSold    isEndingSoon    validFrom    __typename  }  incentiveText  isIncentiveCashback  isNew  isSalesPromotion  hideInProductDiscovery  canAddToBasket  hidePrice  insteadOfPrice {    type    price {      amountIncl      amountExcl      currency      fraction      __typename    }    __typename  }  minOrderQuantity  __typename}"}]
                )
            except Exception as e:
                log(e)
                continue
            
            if r.status_code == 200:
                self.allproducts = r.json()
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
            if differentCard["delivery"] not in ["UNKNOWN", "LAUNCH"]:
                self.differentCard = differentCard
                self.getStockx()
                self.sendWebhook()
                worth = self.checkWorth()
                if worth:
                    sendEveryoneWebhook()
                    self.startBot(differentCard["productId"])

            else:
                log("Found Change but is bad {} {}".format(differentCard["name"],differentCard["delivery"]))
        self.allCardsOld = self.allCards
        

    def checkWorth(self):
        if self.differentCard["delivery"] == "ONEDAY":
            noSpace = self.differentCard["name"].replace(" ", "").lower()

            if "3070ti" in noSpace and 750 > int(self.differentCard["price"]):
                return True

            if "3070" in noSpace and "ti" not in noSpace and 750 > int(self.differentCard["price"]):
                return True

            if "3080" in noSpace and "ti" not in noSpace and 1200 > int(self.differentCard["price"]):
                return True

        return False

    def startBot(self, cardId):
        while True:
            try:
                r = requests.get(
                url=f'http://127.0.0.1:5000/calixio/api/quicktask?module=digitec&url={cardId}',
                headers={
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                })
            except Exception as e:
                log(e)
                log("Failed to Reach Bot")
                break
            
            if r.status_code == 200:
                log(f"Started Bot with {cardId}")
                break
            else:
                log(r.status_code)
                log(r.text)
                log("Failed to Reach Bot")
                break

    def start(self):
        self.firstTime = True
        while True:
            self.getProducts()
            self.compareCards()
            time.sleep(5)
            self.firstTime = False

monitor().start()