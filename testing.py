import requests
import json

# re = requests.get("http://127.0.0.1:5000/all_products")

sale = {
        "user_id": 1,
        "products": [{
            "product_name": "Cookies",
            "quantity": 2,
            "product_discount_per": 0,
            "product_discount_desc": "None"
        },
        {
            "product_name": "Lemonade",
            "quantity": 3,
            "product_discount_per": 0,
            "product_discount_desc": "None"
        }],
        "sale_discount_per": 0,
        "sale_discount_desc": "None"
    }



# print(json.loads(re.content))
# print("\n\n\n\n\n")
# print(re.status_code)


print(requests.put("http://127.0.0.1:5000/data/place_order",json={"data":str(sale)}).content)