#!/bin/bash

# Nombre de la tabla
TABLE_NAME="Transactions"

# Región donde se creará la tabla (modificar según necesidad)
AWS_REGION="us-east-1"

# Crear la tabla en DynamoDB
aws --profile vendemas-dev dynamodb create-table \
    --table-name "Transactions" \
    --attribute-definitions \
        AttributeName=transaction_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=N \
    --key-schema \
        AttributeName=transaction_id,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region "us-east-1"

# Verificar si la tabla fue creada correctamente
if [ $? -eq 0 ]; then
    echo "✅ La tabla '$TABLE_NAME' se ha creado exitosamente en la región '$AWS_REGION'."
else
    echo "❌ Error al crear la tabla '$TABLE_NAME'."
fi




