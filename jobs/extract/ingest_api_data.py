import os
import json
import requests
import boto3
from datetime import datetime, timezone

# Configuration du client S3 (Localstack)
s3 = boto3.client(
    's3',
    endpoint_url='http://localstack:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

BUCKET_NAME = 'my-bucket'
RAW_FOLDER = 'raw'

try:
    s3.create_bucket(Bucket=BUCKET_NAME)
except s3.exceptions.BucketAlreadyOwnedByYou:
    pass
except Exception as e:
    print("Erreur création bucket:", e)

def sanitize_filename(filename):
    """ Remplace les caractères spéciaux interdits pour éviter les erreurs. """
    return filename.replace(":", "-").replace("+", "").replace(" ", "_")

def fetch_weather_data():
    """ Récupère les données météo et les stocke en S3 """
    url = "https://api.open-meteo.com/v1/forecast?latitude=48.8566&longitude=2.3522&hourly=temperature_2m"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    timestamp = datetime.now(timezone.utc).isoformat()
    filename = sanitize_filename(f"weather_{timestamp}.json")
    local_path = os.path.join("/tmp", filename)

    with open(local_path, "w") as f:
        json.dump(data, f)

    s3.upload_file(local_path, BUCKET_NAME, f"{RAW_FOLDER}/{filename}")
    return filename

def fetch_bike_data():
    """ Récupère les données Vélib' et les stocke en S3 """
    url = "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_status.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    timestamp = datetime.now(timezone.utc).isoformat()
    filename = sanitize_filename(f"bike_{timestamp}.json")
    local_path = os.path.join("/tmp", filename)

    with open(local_path, "w") as f:
        json.dump(data, f)

    s3.upload_file(local_path, BUCKET_NAME, f"{RAW_FOLDER}/{filename}")
    return filename

if __name__ == '__main__':
    fetch_weather_data()
    fetch_bike_data()
