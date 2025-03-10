from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.ml.feature import VectorAssembler, StringIndexerModel
from pyspark.ml.regression import LinearRegressionModel
from elasticsearch import Elasticsearch, helpers
from pyspark.sql.functions import col, date_trunc, broadcast

def predict_bike_availability():

    conf = SparkConf() \
        .setAppName("BikeAvailabilityPrediction") \
        .setMaster("local[*]") \
        .set("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.2,com.amazonaws:aws-java-sdk-bundle:1.11.375") \
        .set("spark.hadoop.fs.s3a.endpoint", "http://localstack:4566") \
        .set("spark.hadoop.fs.s3a.access.key", "test") \
        .set("spark.hadoop.fs.s3a.secret.key", "test") \
        .set("spark.hadoop.fs.s3a.path.style.access", "true") \
        .set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .set("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .set("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")

    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    AGG_PATH = "s3a://my-bucket/agg/"
    MODEL_PATH = "s3a://my-bucket/models/spark_lr_model"
    INDEXER_PATH = "s3a://my-bucket/models/station_indexer"

    df_agg = spark.read.parquet(AGG_PATH)

    required_columns = {"station_id", "station_name", "hour", "avg_temperature"}
    if not required_columns.issubset(set(df_agg.columns)):
        raise ValueError(f"Les colonnes attendues sont absentes dans `agg`: {set(df_agg.columns)}")

    model = LinearRegressionModel.load(MODEL_PATH)
    indexer = StringIndexerModel.load(INDEXER_PATH)

    df_agg = indexer.transform(df_agg)

    assembler = VectorAssembler(inputCols=["avg_temperature", "station_index"], outputCol="features")
    df_agg = assembler.transform(df_agg)

    predictions = model.transform(df_agg).select("station_name", "hour", "prediction")

    predictions = predictions.withColumnRenamed("prediction", "predicted_available_bikes")
    predictions = predictions.withColumn("predicted_available_bikes", col("predicted_available_bikes").cast("double"))

    es = Elasticsearch(hosts=["http://elasticsearch:9200"])

    actions = [
        {
            "_index": "velib_predictions",
            "_source": {
                "station_name": row.station_name,
                "hour": row.hour.isoformat(),
                "predicted_available_bikes": max(0, row.predicted_available_bikes) 
            }
        }
        for row in predictions.collect()
    ]

    if actions:
        helpers.bulk(es, actions)
        print("Prédictions indexées avec succès dans Elasticsearch")

    spark.stop()

if __name__ == "__main__":
    predict_bike_availability()
