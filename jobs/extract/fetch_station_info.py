import requests
import json
import boto3
from datetime import datetime, timezone

s3 = boto3.client(
    's3',
    endpoint_url='http://localstack:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

BUCKET_NAME = 'my-bucket'
STATION_INFO_PATH = 'raw/station_info.json'

def fetch_station_info():
    url = "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_information.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    timestamp = datetime.now(timezone.utc).isoformat()
    filename = f"station_info_{timestamp}.json"
    local_path = f"/tmp/{filename}"

    with open(local_path, "w") as f:
        json.dump(data, f)

    s3.upload_file(local_path, BUCKET_NAME, STATION_INFO_PATH)
    return filename

if __name__ == '__main__':
    fetch_station_info()
