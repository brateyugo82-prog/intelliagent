import json
from utils.meta_api import upload_product_to_meta

def publish_mtm_catalog():
    catalog_path = "backend/clients/mtm_client/output/catalog/mtm_catalog.json"
    
    with open(catalog_path, "r", encoding="utf-8") as f:
        products = json.load(f)
    
    for product in products:
        upload_product_to_meta(product)

if __name__ == "__main__":
    publish_mtm_catalog()
