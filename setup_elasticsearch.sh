#!/bin/bash

echo "Attente de Elasticsearch..."
until curl -s -X GET "http://elasticsearch:9200/_cluster/health?wait_for_status=yellow&timeout=30s" | grep -q '"status":"yellow"\|"status":"green"'; do
  sleep 5
  echo "Elasticsearch n'est pas encore prêt..."
done

echo "Elasticsearch est prêt. Configuration en cours..."

# Suppression de l'index s'il existe déjà
curl -X DELETE "http://elasticsearch:9200/velib_agg"

# Création de l'index avec mapping
curl -X PUT "http://elasticsearch:9200/velib_agg" -H "Content-Type: application/json" -d '
{
  "mappings": {
    "properties": {
      "station_id": { "type": "long" },
      "station_name": { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
      "hour": { "type": "date" },
      "avg_available_bikes": { "type": "float" },
      "avg_temperature": { "type": "float" },
      "record_count": { "type": "long" },
      "location": { "type": "geo_point" }
    }
  }
}'

echo "Elasticsearch est configuré avec succès !"
