from datetime import datetime
import logging
import os
import uuid
import requests
import boto3
import json

URL_EPD_INFOS = "https://data.eco-platform.org/resource/processes"
UUID_KEY = "uuid"
URI_KEY = "uri"
EPD_VERSION_KEY = "version"

BUCKET_NAME = os.getenv("BUCKET_NAME")
FOLDER_NAME = "eco"

s3 = boto3.client("s3")
ssm = boto3.client("ssm", region_name="eu-west-3")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_all_epd_infos() -> list:
    headers = {"Authorization": f"Bearer {get_api_token()}"}
    current_year = datetime.now().year
    params = {
        "search": "true",
        "format": "json",
        "distributed": "true",
        "virtual": "true",
        "metaDataOnly": "false",
        "validUntil": current_year,
    }
    try:
        response = requests.get(URL_EPD_INFOS, headers=headers, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error while getting all EPDs infos: {e}")
        raise e

    json_response = response.json()
    datas = json_response["data"]
    total_count = json_response["totalCount"]
    page_size = json_response["pageSize"]
    start_index = json_response["startIndex"] + page_size

    logger.info(f"Retrieved initial page with {len(datas)} records.")

    while start_index < total_count:
        params["startIndex"] = start_index
        response = requests.get(URL_EPD_INFOS, headers=headers, params=params)

        try:
            response = requests.get(URL_EPD_INFOS, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error while getting EPD infos at index {start_index}: {e}")
            return datas

        json_response = response.json()
        datas += json_response["data"]
        start_index = json_response["startIndex"] + page_size

    epd_infos = [
        {key: data[key] for key in [UUID_KEY, URI_KEY, EPD_VERSION_KEY]}
        for data in datas
    ]
    logger.info(f"Total EPD infos retrieved: {len(epd_infos)}")
    return epd_infos


def get_api_token() -> str:
    parameter_name = "/etl/ECOPLATFORM_TOKEN"
    try:
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=False)
        return response["Parameter"]["Value"]
    except Exception as e:
        logger.error(f"Error retrieving API token: {e}")
        raise e


def upload_batch_to_s3(batch_data):
    batch_id = str(uuid.uuid4())
    s3_key = f"batches/{FOLDER_NAME}/{batch_id}.json"
    s3.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=json.dumps(batch_data))
    return {"s3Key": s3_key}


def lambda_handler(event, context) -> list:
    epd_infos = get_all_epd_infos()
    batch_size = 200
    s3_keys = []
    for i in range(0, len(epd_infos), batch_size):
        curr_batch_size = min(batch_size, len(epd_infos) - i)
        batch_data = {
            "batchId": i // batch_size,
            "epdInfos": epd_infos[i : i + curr_batch_size],
        }
        s3_keys.append(upload_batch_to_s3(batch_data))

    return {"inputBatchesS3Keys": s3_keys}
