import requests
import json

# URL d'Elasticsearch
ELASTICSEARCH_URL = "http://localhost:9200"
INDEX_NAME = "velib_agg"

MAPPING = {
    "mappings": {
        "properties": {
            "station_id": {"type": "long"},
            "station_name": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword", "ignore_above": 256}
                }
            },
            "hour": {"type": "date"},
            "avg_available_bikes": {"type": "float"},
            "avg_temperature": {"type": "float"},
            "record_count": {"type": "long"},
            "location": {"type": "geo_point"}
        }
    }
}

def setup_elasticsearch():
    """Supprime l'index s'il existe et le recrée avec le bon mapping"""
    # Vérifier si l'index existe
    response = requests.get(f"{ELASTICSEARCH_URL}/{INDEX_NAME}")
    
    if response.status_code == 200:
        print(f"L'index {INDEX_NAME} existe déjà, suppression en cours...")
        requests.delete(f"{ELASTICSEARCH_URL}/{INDEX_NAME}")
        print(f"Index {INDEX_NAME} supprimé.")

    # Création du nouvel index avec mapping
    print(f"🚀 Création du nouvel index `{INDEX_NAME}` avec `geo_point`...")
    response = requests.put(
        f"{ELASTICSEARCH_URL}/{INDEX_NAME}",
        headers={"Content-Type": "application/json"},
        data=json.dumps(MAPPING)
    )

    if response.status_code == 200:
        print(f"Index `{INDEX_NAME}` créé avec succès !")
    else:
        print(f"Erreur lors de la création de l'index : {response.text}")

if __name__ == "__main__":
    setup_elasticsearch()
