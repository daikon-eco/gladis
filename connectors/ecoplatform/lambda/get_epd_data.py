import json
import os
import requests
import boto3
from botocore.exceptions import ClientError
import logging


URL_EPD_INFOS = "https://data.eco-platform.org/resource/processes"
UUID_KEY = "uuid"
URI_KEY = "uri"
DATASET_VERSION_KEY = "dataset_version"
EPD_VERSION_KEY = "version"
PDF_URL_KEY = "pdf_url"
ERROR_KEY = "error"
BUCKET_NAME = os.getenv("BUCKET_NAME")
FOLDER_NAME = "eco"

s3 = boto3.client("s3")
ssm = boto3.client("ssm", region_name="eu-west-3")


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_epd_data(epd_info: dict) -> dict:
    uuid, uri, version = (
        epd_info[UUID_KEY],
        epd_info[URI_KEY],
        epd_info[EPD_VERSION_KEY],
    )
    uri = uri.replace(" ", "")
    headers = {"Authorization": f"Bearer {get_api_token()}"}
    params = {
        "format": "json",
    }
    response = requests.get(uri, headers=headers, params=params)
    try:
        epd_data = response.json()
        epd_data[PDF_URL_KEY] = get_pdf_url(uri, uuid, version)
        epd_data[UUID_KEY] = uuid
        epd_data[URI_KEY] = uri
        epd_data[DATASET_VERSION_KEY] = version
        epd_data[ERROR_KEY] = False
    except Exception as e:
        epd_data = {
            UUID_KEY: uuid,
            URI_KEY: uri,
            DATASET_VERSION_KEY: version,
            ERROR_KEY: True,
        }
        logger.warning(f"Error retrieving data for UUID: {uuid} - {e}")

    return epd_data


def get_api_token() -> str:
    parameter_name = "/etl/ECOPLATFORM_TOKEN"
    try:
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=False)
        return response["Parameter"]["Value"]
    except Exception as e:
        logger.error(f"Error retrieving API token: {e}")
        raise e


def get_pdf_url(uri: str, uuid: str, version: str) -> str:
    base_url = uri.split("resource/")[0] + "resource/processes"
    url = f"{base_url}/{uuid}/epd"
    if version:
        url += f"?version={version}"
    return url


def save_epd_data_to_s3(epd_data: dict):
    errors_count, duplicates_count = 0, 0
    if epd_data.get(ERROR_KEY):
        errors_count += 1
        logger.warning(f"Error while retrieving data for EPD: {epd_data}")
    else:
        uuid = epd_data[UUID_KEY]
        if is_object_in_s3(uuid):
            logger.info(f"EPD with UUID {uuid} already saved in S3")
            # TODO: Update instead of ignoring
            duplicates_count += 1
        else:
            metadata = {
                DATASET_VERSION_KEY: epd_data[DATASET_VERSION_KEY],
                EPD_VERSION_KEY: epd_data[EPD_VERSION_KEY],
                URI_KEY: epd_data[URI_KEY],
                UUID_KEY: epd_data[UUID_KEY],
                PDF_URL_KEY: epd_data[PDF_URL_KEY],
            }
            s3.put_object(
                Body=json.dumps(epd_data),
                Bucket=BUCKET_NAME,
                Key=get_epd_json_file_key(uuid),
                Metadata=metadata,
                ContentType="application/json",
            )
    return errors_count, duplicates_count


def get_epd_json_file_name(id: str) -> str:
    return f"{id}.json"


def get_epd_json_file_key(id) -> str:
    return f"{FOLDER_NAME}/{get_epd_json_file_name(id)}"


def is_object_in_s3(id: str) -> bool:
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=get_epd_json_file_key(id))
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            raise Exception(f"Error while checking if EPD is already is s3: {e}")


def get_batch_data_from_s3(s3_key: str) -> list:
    response = s3.get_object(Bucket=BUCKET_NAME, Key=s3_key)
    batch_data = json.loads(response["Body"].read().decode("utf-8"))
    return batch_data["batchId"], batch_data["epdInfos"]


def remove_batch_data_from_s3(s3_key: str):
    s3.delete_object(Bucket=BUCKET_NAME, Key=s3_key)


def lambda_handler(event: str, context):
    errors_count, duplicates_count = 0, 0
    batch_id, epd_infos = get_batch_data_from_s3(event["s3Key"])
    for epd_info in epd_infos:
        epd_data = get_epd_data(epd_info)
        curr_errors, curr_duplicates = save_epd_data_to_s3(epd_data)
        errors_count += curr_errors
        duplicates_count += curr_duplicates

    logger.info(
        f"Processed batch of {len(epd_infos)} records, with {errors_count} errors and {duplicates_count} duplicates."
    )
    remove_batch_data_from_s3(event["s3Key"])

    return {
        "batchId": batch_id,
        "errorsCount": errors_count,
        "duplicatesCount": duplicates_count,
    }
