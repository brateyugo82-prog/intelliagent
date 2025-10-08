import requests
import os

GRAPH_BASE = "https://graph.facebook.com/v19.0"

def upload_product_to_meta(product: dict):
    token = os.getenv("META_ACCESS_TOKEN")
    catalog_id = os.getenv("META_CATALOG_ID")
    url = f"{GRAPH_BASE}/{catalog_id}/items"
    
    payload = {
        "retailer_id": str(product["id"]),
        "name": product["title"],
        "description": product["description"],
        "price": f"{product['price']} EUR",
        "availability": product.get("availability", "in stock"),
        "condition": "new",
        "image_url": product["image_link"],
        "url": product["link"],
        "brand": "MTM"
    }
    
    r = requests.post(url, params={"access_token": token}, data=payload)
    if r.status_code != 200:
        print(f"❌ Fehler bei {product['title']}: {r.text}")
    else:
        print(f"✅ Produkt '{product['title']}' erfolgreich hochgeladen.")
    return r.json()
