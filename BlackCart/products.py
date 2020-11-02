import os
from pathlib import Path

from flask import Flask, jsonify, abort
import json
from settings import FlaskConfig

app = Flask(__name__)
app.config.from_object(FlaskConfig)

"""
    get_products does the following:
     1) Gets the store based on store ID
     2) Parses the  products from respective stores using json(shopifyproducts, woocommerce) provided in mockup data 
     3) Generates the json response in the following format:
        {
            "Name": "IPod Nano - 8GB", 
            "ProductId": 632910392,
            "Variations": [
              {
                "currency": "USD", 
                "inventory_status": "in_stock", 
                "name": "Color", 
                "price": "199.00", 
                "title": "Pink", 
                "weight": 1.25
              }, 
              {
                "currency": "USD", 
                "inventory_status": "in_stock", 
                "name": "Color", 
                "price": "199.00", 
                "title": "Red", 
                "weight": 1.75
              }, 
              {
                "currency": "USD", 
                "inventory_status": "in_stock", 
                "name": "Color", 
                "price": "199.00", 
                "title": "Green", 
                "weight": 1.25
              }, 
              {
                "currency": "USD", 
                "inventory_status": "in_stock", 
                "name": "Color", 
                "price": "199.00", 
                "title": "Black", 
                "weight": 1.25
              }]
        }
        
        wherein 
        Name -> name of the product
        ProductId -> id of the product
        Variations -> defines the following:
                        i)   Currency (like USD, CAd)
                        ii)  inventory_status (instock, outofstock)
                        iii) name is the name of the variant which will be added for each value to determine the type of the value
                        iv)  price determines the price of the item in the mentioned currency above
                        v)   title is the title of the variation in this case color
                        vi)  weight is the corresponding weight of the item
                        
        Due to time constraints the if conditions regarding the platform check is not modified further, 
        we can create separate functions where we can generalize the code to avoid repetitive conditions and statements      
"""
@app.route('/stores/<storeID>/products', methods=["GET"])
def get_products(storeID):
    base_path = Path(__file__)
    stores_file_path = (base_path / "../mock_data/stores.json").resolve()
    store_data = None
    try:
        with open(stores_file_path) as f:
            data = json.load(f)
            for store in data["stores"]:
                try:
                    if int(store["id"]) == int(storeID):
                        store_data = store
                        break
                except:
                    store_data = None
                    break

            if store_data is None:
                abort(404, description="Store not found")

            product_details = []
            if int(store_data["id"]) == 1 and store_data["platform"] == "shopify":
                shopify_file_path = (base_path / "../mock_data/shopifyproducts.json").resolve()
                with(open(shopify_file_path)) as f:
                    shopify_data = json.load(f)
                    if len(shopify_data["products"]) <= 0:
                        abort(404, description="Products not found")

                    for product in shopify_data["products"]:
                        variations = []
                        for option in product["options"]:
                            for value in option["values"]:
                                variations.append({
                                    'name': option['name'],
                                    'title': value,
                                    'weight': None,
                                    'inventory_status': None,
                                    'price': None,
                                    'currency': "USD"
                                })

                        for variants in product['variants']:
                            for variation in variations:
                                if variants['title'] == variation['title']:
                                    variation['weight'] = variants['weight']
                                    if variants['inventory_quantity'] > 0:
                                        variation['inventory_status'] = "instock"
                                    else:
                                        variation['inventory_status'] = "outofstock"
                                    for price in variants['presentment_prices']:
                                        variation['price'] = price["price"]["amount"]
                                        variation['currency'] = price["price"]["currency_code"]
                                    break

                        product_details.append({
                            "Name": product["title"],
                            "ProductId": product["id"],
                            "Variations" : variations
                        })

            elif int(store_data["id"]) == 2 and store_data["platform"] == "woocommerce":
                woocommerce_file_path = (base_path / "../mock_data/woocommerce.json").resolve()
                with(open(woocommerce_file_path)) as f:
                    woocommerce_data = json.load(f)
                    if len(woocommerce_data) <=0 :
                        abort(404, description="Products not found")
                    for product in woocommerce_data:
                        variations = []
                        variations.append({
                            'name': product["name"],
                            'title': product["name"],
                            'weight': product["weight"],
                            'inventory_status': product["stock_status"],
                            'price': product["price"],
                            'currency': "USD"
                        })
                        product_details.append({
                                "Name": product["name"],
                                "ProductId": product["id"],
                                "Variations": variations
                            })

            return jsonify(product_details)

    except FileNotFoundError:
        abort(404, description="File not found")


"""
    Custom error handler to handle various conditions like 
    product not found, store not found, or in this case file not found to give a clear message to the user
"""
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e.code) + ": " + str(e.description)), 404