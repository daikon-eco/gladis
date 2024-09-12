from datetime import datetime
import requests
from tqdm import tqdm
import os
import pymongo
import concurrent.futures


URL_EPD_INFOS = "https://data.eco-platform.org/resource/processes"
LOCAL_MONGO_URL = "mongodb://localhost:27017/"
MONGO_DB_NAME = "epd_data"
MONGO_COLLECTION_NAME = "epd_ecoplatform"
API_TOKEN = os.getenv("ECO_PLATFORM_TOKEN")


class EcoPlatform:
    def __init__(self, mongo_db_url: str, db_name: str, collection_name: str):
        self.client = pymongo.MongoClient(mongo_db_url)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def get_all_epd_infos(self) -> list:
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        current_year = datetime.now().year
        params = {
            "search": "true",
            "format": "json",
            "distributed": "true",
            "virtual": "true",
            "metaDataOnly": "false",
            "validUntil": current_year,
        }
        response = requests.get(URL_EPD_INFOS, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error while getting all EPDs infos: {response.status_code}")
            return []

        json_response = response.json()
        datas = json_response["data"]
        total_count = json_response["totalCount"]
        page_size = json_response["pageSize"]
        start_index = json_response["startIndex"] + page_size

        while start_index < total_count:
            params["startIndex"] = start_index
            response = requests.get(URL_EPD_INFOS, headers=headers, params=params)

            if response.status_code != 200:
                print(f"Error while getting all EPDs infos: {response.status_code}")
                return datas

            json_response = response.json()
            datas += json_response["data"]
            start_index = json_response["startIndex"] + page_size

        self.epd_infos = [
            {key: data[key] for key in ["uuid", "uri", "version"]} for data in datas
        ]
        return self.epd_infos

    def get_epd_data(self, epd_info: dict) -> dict:
        uuid, uri, version = epd_info["uuid"], epd_info["uri"], epd_info["version"]
        uri = uri.replace(" ", "")
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        params = {
            "format": "json",
        }
        response = requests.get(uri, headers=headers, params=params)
        try:
            epd_data = response.json()
            epd_data["pdf_url"] = self.get_pdf_url(uri, uuid, version)
            epd_data["_id"] = uuid
            epd_data["uri"] = uri
            epd_data["dataset_version"] = version
            epd_data["error"] = False
        except Exception:
            epd_data = {
                "_id": uuid,
                "uri": uri,
                "dataset_version": version,
                "error": True,
            }

        return epd_data

    @staticmethod
    def get_pdf_url(uri: str, uuid: str, version: str) -> str:
        base_url = uri.split("resource/")[0] + "resource/processes"
        url = f"{base_url}/{uuid}/epd"
        if version:
            url += f"?version={version}"
        return url

    def save_all_epd_data(self, max_workers: int = 8) -> list:
        errors_count = 0
        duplicates_count = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            print("Start importing data to MongoDB..")
            futures = [
                executor.submit(self.get_epd_data, epd_info)
                for epd_info in self.epd_infos
            ]
            with tqdm(total=len(futures)) as pbar:
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    pbar.update(1)
                    if result.get("error"):
                        errors_count += 1
                        print(f"Error while retrieving data for EPD: {result}")
                    else:
                        _id = result["_id"]
                        if self.collection.find_one({"_id": _id}):
                            print(
                                f"EPD with UUID {_id} already exists in the collection"
                            )
                            self.collection.update_one({"_id": _id}, {"$set": result})
                            duplicates_count += 1
                        else:
                            self.collection.insert_one(result)
            print(
                f"..Finished importing data to MongoDB. {errors_count} errors and {duplicates_count} duplicates were found."
            )


if __name__ == "__main__":
    crawler = EcoPlatform(LOCAL_MONGO_URL, MONGO_DB_NAME, MONGO_COLLECTION_NAME)
    crawler.save_all_epd_data()
