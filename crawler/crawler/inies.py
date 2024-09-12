import json
import random

import pymongo
import requests
from tqdm import tqdm

URL_BASE_INIES = "https://www.base-inies.fr"
URL_BASE_INIES_API = f"{URL_BASE_INIES}/iniesV4/dist"
LOCAL_MONGO_URL = "mongodb://localhost:27017/"
MONGO_DB_NAME = "epd_data"
MONGO_COLLECTION_NAME = "epd_inies"


class Inies:
    def __init__(self, mongo_db_url: str, db_name: str, collection_name: str):
        self.client = pymongo.MongoClient(mongo_db_url)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    @staticmethod
    def get_all_product_ids() -> list:
        url = f"{URL_BASE_INIES_API}/api/SearchProduits"
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.6",
            "content-type": "application/json",
            "dnt": "1",
            "origin": URL_BASE_INIES,
            "priority": "u=1, i",
            "referer": f"{URL_BASE_INIES_API}/recherche-fdes",
            "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Brave";v="128"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        }
        data = json.dumps(
            {
                "typeDeclaration": 0,
                "cov": 0,
                "onlineDate": 0,
                "lieuProduction": 0,
                "perfUF": 0,
                "norme": 0,
                "onlyArchive": False,
            }
        )
        return requests.post(url, headers=headers, data=data).json()

    @staticmethod
    def get_product_response(id: int) -> requests.Response:
        product_url = f"{URL_BASE_INIES_API}/api/Produit/{id}"
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "priority": "u=1, i",
            "referer": f"{URL_BASE_INIES_API}/infos-produit",
            "sec-ch-ua": '"Not;A=Brand";v="24", "Chromium";v="128"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        }
        return requests.get(product_url, headers=headers)

    def save_all_products_data(self):
        ids = self.get_all_product_ids()
        random.shuffle(ids)

        for id in tqdm(ids):
            response = self.get_product_response(id)
            if response.status_code == 200:
                json_data = response.json()
                json_data["_id"] = id
                self.collection.insert_one(json_data)
            else:
                print(f"Failed to retrieve product {id}: {response.status_code}")


if __name__ == "__main__":
    inies = Inies(LOCAL_MONGO_URL, MONGO_DB_NAME, MONGO_COLLECTION_NAME)
    inies.save_all_products_data()
