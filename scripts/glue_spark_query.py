import sys
import boto3
import pandas as pd
from awsglue.context import GlueContext
from pyspark.sql import SparkSession
from awsglue.utils import getResolvedOptions

# Parámetros del job (recibir bucket como parámetro opcional en Glue)
args = getResolvedOptions(sys.argv, ['S3_BUCKET'])
S3_BUCKET = args['S3_BUCKET']  # Bucket S3 donde se subirá el archivo

# Configuración de Spark y Glue
spark = SparkSession.builder.config("spark.sql.catalogImplementation", "hive").getOrCreate()
glueContext = GlueContext(spark.sparkContext)

# Leer la tabla de Glue Catalog
df = spark.sql("""
    SELECT 
        partition_0 AS year,
        partition_1 AS month,
        partition_2 AS day,
        partition_3 AS hour,
        dynamodb.keys.transaction_id.s AS transaction_id, 
        dynamodb.keys.timestamp.n AS timestamp, 
        dynamodb.newimage.amount.n AS amount, 
        dynamodb.newimage.currency.s AS currency, 
        dynamodb.newimage.payment_method.s AS payment_method, 
        dynamodb.newimage.status.s AS status
    FROM dev_test_cdc_s3
    WHERE partition_0 = '2025' 
      AND partition_1 = '02'
      AND partition_3 = '20';
""")

# Convertir a Pandas para guardarlo como CSV
df_pandas = df.toPandas()

# Definir el nombre del archivo CSV
csv_filename = "/tmp/dev_test_cdc_s3_filtered.csv"

# Guardar en formato CSV
df_pandas.to_csv(csv_filename, index=False)

print(f"✅ Archivo CSV generado: {csv_filename}")

# Subir a S3
s3_client = boto3.client('s3')
s3_key = "exports/dev_test_cdc_s3_filtered.csv"  # Ruta dentro del bucket

s3_client.upload_file(csv_filename, S3_BUCKET, s3_key)

print(f"✅ Archivo subido a S3: s3://{S3_BUCKET}/{s3_key}")
