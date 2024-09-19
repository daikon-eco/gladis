from datetime import datetime
import json
import requests
from tqdm import tqdm
import os
import boto3
from botocore.exceptions import ClientError
import concurrent.futures


URL_EPD_INFOS = "https://data.eco-platform.org/resource/processes"
API_TOKEN = os.getenv("ECO_PLATFORM_TOKEN")
UUID_KEY = "uuid"
URI_KEY = "uri"
DATASET_VERSION_KEY = "dataset_version"
EPD_VERSION_KEY = "version"
PDF_URL_KEY = "pdf_url"
ERROR_KEY = "error"


class EcoPlatform:
    def __init__(self):
        self.s3 = boto3.client("s3")
        self.bucket_name = "gladis-epd-raw-data-prod-eu-west-3"
        self.folder_name = "ecoplatform"

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
            {key: data[key] for key in [UUID_KEY, URI_KEY, EPD_VERSION_KEY]}
            for data in datas
        ]
        return self.epd_infos

    def get_epd_data(self, epd_info: dict) -> dict:
        uuid, uri, version = (
            epd_info[UUID_KEY],
            epd_info[URI_KEY],
            epd_info[EPD_VERSION_KEY],
        )
        uri = uri.replace(" ", "")
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        params = {
            "format": "json",
        }
        response = requests.get(uri, headers=headers, params=params)
        try:
            epd_data = response.json()
            epd_data[PDF_URL_KEY] = self.get_pdf_url(uri, uuid, version)
            epd_data[UUID_KEY] = uuid
            epd_data[URI_KEY] = uri
            epd_data[DATASET_VERSION_KEY] = version
            epd_data[ERROR_KEY] = False
        except Exception:
            epd_data = {
                UUID_KEY: uuid,
                URI_KEY: uri,
                DATASET_VERSION_KEY: version,
                ERROR_KEY: True,
            }

        return epd_data

    @staticmethod
    def get_pdf_url(uri: str, uuid: str, version: str) -> str:
        base_url = uri.split("resource/")[0] + "resource/processes"
        url = f"{base_url}/{uuid}/epd"
        if version:
            url += f"?version={version}"
        return url

    def save_all_epd_data_to_s3(self, max_workers: int = 8) -> list:
        errors_count = 0
        duplicates_count = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            print("Start importing data to S3..")
            futures = [
                executor.submit(self.get_epd_data, epd_info)
                for epd_info in self.epd_infos
            ]
            with tqdm(total=len(futures)) as pbar:
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    pbar.update(1)
                    if result.get(ERROR_KEY):
                        errors_count += 1
                        print(f"Error while retrieving data for EPD: {result}")
                    else:
                        uuid = result[UUID_KEY]
                        if self.check_object_in_s3(id):
                            print(
                                f"EPD with UUID {uuid} already exists in the collection"
                            )
                            duplicates_count += 1
                        metadata = {
                            DATASET_VERSION_KEY: result[DATASET_VERSION_KEY],
                            EPD_VERSION_KEY: result[EPD_VERSION_KEY],
                            URI_KEY: result[URI_KEY],
                            UUID_KEY: result[UUID_KEY],
                        }
                        self.s3.put_object(
                            Body=json.dumps(result),
                            Bucket=self.bucket,
                            Key=self.get_epd_json_file_key(uuid),
                            Metadata=metadata,
                            ContentType="application/json",
                        )
            print(
                f"..Finished importing data to S3. {errors_count} errors and {duplicates_count} duplicates were found."
            )

    @staticmethod
    def get_epd_json_file_name(id: str) -> str:
        return f"{id}.json"

    def get_epd_json_file_key(self, id) -> str:
        return f"{self.folder_name}/{self.get_epd_json_file_name(id)}"

    def check_object_in_s3(self, id: str) -> bool:
        try:
            self.s3.head_object(
                Bucket=self.bucket_name, Key=self.get_epd_json_file_key(id)
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                raise e


if __name__ == "__main__":
    crawler = EcoPlatform()
    crawler.save_all_epd_data()
