import json
from dataclasses import dataclass, asdict
from threading import Thread
import lxml
from datetime import datetime, timedelta
from dhooks import Webhook, Embed
import requests
import time
import pymongo
import random

from requests.models import Response


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
        logmsg = logmsg + ""
        with open ('logging.txt', 'a', newline="") as f:
            f.write(logmsg)
    except:
        print("Can't save")



def find_all_products(allproducts):
    allProducts = allproducts[0]["data"]["productType"]["filterProductsV4"]["products"]["resultsWithDefaultOffer"]

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
        print(asdict(card))
  

def getProducts():
    while True:
        try:
            r = requests.get(
            url='https://www.digitec.ch/api/graphql',
            headers={
                'user-agent': 'PostmanRuntime/7.28.4',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                str(random.choice(range(11111111111,99999999999))):str(random.choice(range(11111111111,99999999999)))
            },
            json=[{"operationName":"GET_PRODUCT_TYPE_PRODUCTS_AND_FILTERS","variables":{"productTypeId":106,"queryString":"oo=1&pdo=39-347%3A677785%7C39-347%3A677897%7C39-347%3A651564%7C39-347%3A651565%7C39-347%3A722095%7C39-347%3A722097%7C39-347%3A721845%7C39-347%3A721850%7C39-347%3A629038","offset":0,"limit":84,"sort":"BESTSELLER","siteId":"0","sectorId":1},"query":"query GET_PRODUCT_TYPE_PRODUCTS_AND_FILTERS($productTypeId: Int!, $queryString: String!, $offset: Int, $limit: Int, $sort: ProductSort, $siteId: String, $sectorId: Int) {  productType(id: $productTypeId) {    filterProductsV4(queryString: $queryString, offset: $offset, limit: $limit, sort: $sort, siteId: $siteId, sectorId: $sectorId) {      productCounts {        total        filteredTotal        __typename      }      productFilters {        filterGroupType        label        key        tooltip {          ...Tooltip          __typename        }        ...CheckboxFilterGroup        ...RangeSliderFilterGroup        __typename      }      products {        hasMore        resultsWithDefaultOffer {          ...ProductWithOffer          __typename        }        __typename      }      __typename    }    __typename  }}fragment Tooltip on Tooltip {  text  moreInformationLink  __typename}fragment CheckboxFilterGroup on CheckboxFilterGroupV2 {  filterOptions {    ...Filter    __typename  }  __typename}fragment RangeSliderFilterGroup on RangeSliderFilterGroupV2 {  dataPoints {    ...RangeSliderDataPoint    __typename  }  selectedRange {    min    max    __typename  }  optionIdentifierKey  unitAbbreviation  unitDisplayOrder  totalCount  fullRange {    min    max    __typename  }  stepSize  mergeInfo {    isBottomMerged    isTopMerged    __typename  }  __typename}fragment ProductWithOffer on ProductWithOffer {  mandatorSpecificData {    ...ProductMandatorSpecific    __typename  }  product {    ...ProductMandatorIndependent    __typename  }  offer {    ...ProductOffer    __typename  }  __typename}fragment Filter on Filter {  optionIdentifierKey  optionIdentifierValue  label  productCount  selected  tooltip {    ...Tooltip    __typename  }  __typename}fragment RangeSliderDataPoint on RangeSliderDataPoint {  value  productCount  __typename}fragment ProductMandatorSpecific on MandatorSpecificData {  isBestseller  isDeleted  showroomSites  sectorIds  __typename}fragment ProductMandatorIndependent on ProductV2 {  id  productId  name  nameProperties  productTypeId  productTypeName  brandId  brandName  averageRating  totalRatings  totalQuestions  isProductSet  images {    url    height    width    __typename  }  energyEfficiency {    energyEfficiencyColorType    energyEfficiencyLabelText    energyEfficiencyLabelSigns    energyEfficiencyImage {      url      height      width      __typename    }    __typename  }  seo {    seoProductTypeName    seoNameProperties    productGroups {      productGroup1      productGroup2      productGroup3      productGroup4      __typename    }    gtin    __typename  }  lowQualityImagePlaceholder  hasVariants  smallDimensions  basePrice {    priceFactor    value    __typename  }  __typename}fragment ProductOffer on OfferV2 {  id  productId  offerId  shopOfferId  price {    amountIncl    amountExcl    currency    fraction    __typename  }  deliveryOptions {    mail {      classification      futureReleaseDate      __typename    }    pickup {      siteId      classification      futureReleaseDate      __typename    }    detailsProvider {      productId      offerId      quantity      type      __typename    }    __typename  }  label  type  volumeDiscountPrices {    minAmount    price {      amountIncl      amountExcl      currency      __typename    }    isDefault    __typename  }  salesInformation {    numberOfItems    numberOfItemsSold    isEndingSoon    validFrom    __typename  }  incentiveText  isIncentiveCashback  isNew  isSalesPromotion  hideInProductDiscovery  canAddToBasket  hidePrice  insteadOfPrice {    type    price {      amountIncl      amountExcl      currency      fraction      __typename    }    __typename  }  minOrderQuantity  __typename}"}]
            )
        except Exception as e:
            log(e)
            continue
        
        if r.status_code == 200:
            try:
                find_all_products(r.json)
                break

            except Exception as e:
                log(f"Failed to grab userID {e}")
        else:
            print(r.status_code)
            print(r.text)

getProducts()