import sys
import boto3
import pandas as pd
import time
from awsglue.utils import getResolvedOptions

# Obtener parámetros de Glue (Bucket y Base de Datos de Glue Catalog)
args = getResolvedOptions(sys.argv, ['S3_BUCKET', 'GLUE_DATABASE'])
S3_BUCKET = args['S3_BUCKET']
GLUE_DATABASE = args['GLUE_DATABASE']
ATHENA_OUTPUT = f"s3://{S3_BUCKET}/athena-results/"  # Carpeta donde Athena guardará los resultados

# Inicializar cliente de Athena y S3
athena_client = boto3.client('athena')
s3_client = boto3.client('s3')

# Query SQL para Athena
query = """
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
"""

# Ejecutar la consulta en Athena
response = athena_client.start_query_execution(
    QueryString=query,
    QueryExecutionContext={'Database': GLUE_DATABASE},
    ResultConfiguration={'OutputLocation': ATHENA_OUTPUT}
)

# Obtener el ID de la consulta
query_execution_id = response['QueryExecutionId']
print(f"✅ Query en ejecución: {query_execution_id}")

# Esperar hasta que la consulta termine
while True:
    status = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
    state = status['QueryExecution']['Status']['State']
    
    if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
        break
    print("⌛ Esperando resultados...")
    time.sleep(5)  # Espera 5 segundos antes de volver a revisar el estado

# Verificar si la consulta fue exitosa
if state != 'SUCCEEDED':
    raise Exception(f"❌ La consulta falló con estado: {state}")

# Obtener la ubicación del archivo de resultados en S3
output_location = status['QueryExecution']['ResultConfiguration']['OutputLocation']
print(f"✅ Resultados disponibles en: {output_location}")

# Descargar los resultados de Athena
s3_key = output_location.replace(f"s3://{S3_BUCKET}/", "")
local_filename = "/tmp/dev_test_cdc_s3_filtered.csv"

s3_client.download_file(S3_BUCKET, s3_key, local_filename)
print(f"✅ Archivo descargado: {local_filename}")

# Cargar el archivo CSV con Pandas y volver a guardarlo limpio
df = pd.read_csv(local_filename)
df.to_csv(local_filename, index=False)

# Subir el archivo procesado a S3
s3_dest_key = "exports/dev_test_cdc_s3_filtered.csv"
s3_client.upload_file(local_filename, S3_BUCKET, s3_dest_key)

print(f"✅ Archivo final subido a: s3://{S3_BUCKET}/{s3_dest_key}")
