from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, arrays_zip, to_timestamp
from pyspark import SparkConf

def transform_raw_to_fmt():
    conf = SparkConf() \
        .setAppName("TransformRawToFmt") \
        .setMaster("local[*]") \
        .set("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.2,com.amazonaws:aws-java-sdk-bundle:1.11.375") \
        .set("spark.hadoop.fs.s3a.endpoint", "http://localstack:4566") \
        .set("spark.hadoop.fs.s3a.access.key", "test") \
        .set("spark.hadoop.fs.s3a.secret.key", "test") \
        .set("spark.hadoop.fs.s3a.path.style.access", "true") \
        .set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .set("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")

    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    RAW_PATH = "s3a://my-bucket/raw/"
    FMT_PATH = "s3a://my-bucket/fmt/"

    df_raw = spark.read.option("multiline", "true").json(RAW_PATH)

    if "hourly" in df_raw.columns:
        df_weather = df_raw.select(
            explode(arrays_zip(col("hourly.time"), col("hourly.temperature_2m"))).alias("hourly_data")
        ).select(
            col("hourly_data.time").alias("timestamp"),
            col("hourly_data.temperature_2m").alias("temperature")
        )
        df_weather = df_weather.withColumn("timestamp", to_timestamp(col("timestamp")))

        df_weather.write.mode("overwrite").parquet(FMT_PATH + "weather")
        print("Données météo transformées et sauvegardées dans fmt/weather")

    if "data" in df_raw.columns:
        df_bike = df_raw.select(explode("data.stations").alias("station"))
        df_bike = df_bike.select(
            col("station.station_id").alias("station_id"),
            col("station.num_bikes_available").alias("available_bikes"),
            col("station.num_docks_available").alias("available_docks"),
            to_timestamp(col("station.last_reported")).alias("timestamp")
        )
        df_bike.write.mode("overwrite").parquet(FMT_PATH + "bike")
        print("Données Vélib transformées et sauvegardées dans fmt/bike")

    spark.stop()

if __name__ == "__main__":
    transform_raw_to_fmt()
