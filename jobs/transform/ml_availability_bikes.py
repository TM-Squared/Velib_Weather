from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.regression import LinearRegression

def availability_bikes():
    """ Entraîne un modèle Spark ML avec `station_id` et stocke `station_indexer` sur Localstack S3 """
    
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

    required_columns = {"station_id", "avg_temperature", "avg_available_bikes"}
    if not required_columns.issubset(set(df_agg.columns)) or df_agg.count() == 0:
        spark.stop()
        return

    df_agg = df_agg.withColumn("avg_temperature", df_agg["avg_temperature"].cast("double"))
    df_agg = df_agg.withColumn("avg_available_bikes", df_agg["avg_available_bikes"].cast("double"))
    df_agg = df_agg.withColumn("station_id", df_agg["station_id"].cast("string"))  # Encodage en string

    # ✅ Encodage des `station_id`
    indexer = StringIndexer(inputCol="station_id", outputCol="station_index")
    indexer_model = indexer.fit(df_agg)
    df_agg = indexer_model.transform(df_agg)

    # ✅ Sauvegarder `station_indexer`
    indexer_model.write().overwrite().save(INDEXER_PATH)

    # ✅ Création du vecteur de features
    assembler = VectorAssembler(inputCols=["avg_temperature", "station_index"], outputCol="features")
    df_transformed = assembler.transform(df_agg)

    # ✅ Entraînement du modèle
    lr = LinearRegression(featuresCol="features", labelCol="avg_available_bikes")
    model = lr.fit(df_transformed)

    # ✅ Sauvegarde du modèle ML
    model.write().overwrite().save(MODEL_PATH)

    print(f"✅ Modèle ML et station_indexer sauvegardés sur Localstack S3")
    spark.stop()

if __name__ == "__main__":
    availability_bikes()
