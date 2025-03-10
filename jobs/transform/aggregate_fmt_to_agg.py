from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, date_trunc, broadcast, first, struct, concat_ws
from pyspark import SparkConf

def aggregate_fmt_to_agg():
    """ Agrège les données formatées """
    conf = SparkConf() \
        .setAppName("AggregateFmtToAgg") \
        .setMaster("local[*]") \
        .set("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.2,com.amazonaws:aws-java-sdk-bundle:1.11.375") \
        .set("spark.hadoop.fs.s3a.endpoint", "http://localstack:4566") \
        .set("spark.hadoop.fs.s3a.access.key", "test") \
        .set("spark.hadoop.fs.s3a.secret.key", "test") \
        .set("spark.hadoop.fs.s3a.path.style.access", "true") \
        .set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    FMT_PATH = "s3a://my-bucket/fmt/"
    STATION_INFO_PATH = "s3a://my-bucket/raw/station_info.json"
    AGG_PATH = "s3a://my-bucket/agg/"

    df_bike = spark.read.parquet(FMT_PATH + "bike")
    df_weather = spark.read.parquet(FMT_PATH + "weather")

    df_weather = df_weather.withColumn("temperature", col("temperature").cast("double"))

    df_bike = df_bike.withColumn("hour", date_trunc("hour", col("timestamp")))
    df_weather = df_weather.withColumn("hour", date_trunc("hour", col("timestamp")))

    df_station_info = spark.read.option("multiline", "true").json(STATION_INFO_PATH)
    df_stations = df_station_info.selectExpr("explode(data.stations) as station")
    df_stations = df_stations.select(
        col("station.station_id").alias("station_id"),
        col("station.name").alias("station_name"),
        col("station.lat").cast("double").alias("latitude"),  
        col("station.lon").cast("double").alias("longitude")
    )

    df_joined = df_bike.join(df_weather, on="hour", how="inner")
    df_joined = df_joined.join(broadcast(df_stations), on="station_id", how="left")

    df_joined = df_joined.withColumn("location", concat_ws(",", col("latitude"), col("longitude")))

    df_agg = df_joined.groupBy("station_id", "station_name", "hour").agg(
        avg("available_bikes").alias("avg_available_bikes"),
        avg("temperature").alias("avg_temperature"),
        count("*").alias("record_count"),
        first("location").alias("location")
    )

    df_agg.write.mode("overwrite").parquet(AGG_PATH)
    print("Données agrégées et enrichies sauvegardées dans :", AGG_PATH)

    spark.stop()

if __name__ == "__main__":
    aggregate_fmt_to_agg()