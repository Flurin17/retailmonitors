import json
from dataclasses import dataclass, asdict

@dataclass
class Graphicscard:
    productId: int
    name: str
    link: str 
    price: float
    delivery: str
    picture: str

# Opening JSON file
f = open('products.json',)
  
# returns JSON object as 
# a dictionary
data = json.load(f)
  
# Iterating through the json
# list






allProducts = data[0]["data"]["productType"]["filterProductsV4"]["products"]["resultsWithDefaultOffer"]

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
  
# Closing file
f.close()