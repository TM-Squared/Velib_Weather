from pyspark.sql import SparkSession
from pyspark import SparkConf
from elasticsearch import Elasticsearch, helpers

def index_agg_to_elasticsearch():
    """ Charge les données agrégées dans Elasticsearch """
    
    conf = SparkConf() \
        .setAppName("IndexAggToElasticsearch") \
        .setMaster("local[*]") \
        .set("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.2,com.amazonaws:aws-java-sdk-bundle:1.11.375") \
        .set("spark.hadoop.fs.s3a.endpoint", "http://localstack:4566") \
        .set("spark.hadoop.fs.s3a.access.key", "test") \
        .set("spark.hadoop.fs.s3a.secret.key", "test") \
        .set("spark.hadoop.fs.s3a.path.style.access", "true") \
        .set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    AGG_PATH = "s3a://my-bucket/agg/"
    df_agg = spark.read.parquet(AGG_PATH)

    es = Elasticsearch(hosts=["http://elasticsearch:9200"])

    actions = [
        {
            "_index": "velib_agg",
            "_source": {
                "station_id": row.station_id,
                "station_name": row.station_name,
                "hour": row.hour.isoformat(),
                "location": row.location,
                "avg_available_bikes": row.avg_available_bikes,
                "avg_temperature": row.avg_temperature,
                "record_count": row.record_count
            }
        }
        for row in df_agg.collect()
    ]

    if actions:
        helpers.bulk(es, actions)
        print("Indexation terminée avec succès")
    spark.stop()

if __name__ == "__main__":
    index_agg_to_elasticsearch()
