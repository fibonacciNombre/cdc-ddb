#!/bin/bash

# Nombre de la tabla
TABLE_NAME="Transactions"

# Región donde se encuentra la tabla (modificar si es necesario)
AWS_REGION="us-east-1"

# Función para generar un número aleatorio entre un rango
random_number() {
    awk -v min="$1" -v max="$2" 'BEGIN{srand(); print int(min+rand()*(max-min+1))}'
}

# Función para seleccionar un valor aleatorio de una lista
random_choice() {
    echo "$@" | tr ' ' '\n' | sort -R | head -n1
}

# Generar 100 registros aleatorios
for i in {1..100}; do
    TRANSACTION_ID=$(uuidgen)  # Genera un UUID único
    TIMESTAMP=$(date +%s | cut -b1-13)  # Genera timestamp en milisegundos
    AMOUNT=$(random_number 10 1000)  # Monto aleatorio entre 10 y 1000
    CURRENCY=$(random_choice USD EUR GBP CAD JPY AUD)  # Selecciona una moneda aleatoria
    PAYMENT_METHOD=$(random_choice credit_card debit_card paypal bank_transfer crypto)  # Método de pago aleatorio
    STATUS=$(random_choice pending completed failed)  # Estado aleatorio
    
    # Crear el JSON para DynamoDB
    ITEM_JSON=$(cat <<EOF   
{
    "transaction_id": {"S": "$TRANSACTION_ID"},
    "timestamp": {"N": "$TIMESTAMP"},
    "amount": {"N": "$AMOUNT"},
    "currency": {"S": "$CURRENCY"},
    "payment_method": {"S": "$PAYMENT_METHOD"},
    "status": {"S": "$STATUS"}
}
EOF
)

    # Insertar en DynamoDB
    aws --profile vendemas-dev dynamodb put-item --table-name "$TABLE_NAME" --item "$ITEM_JSON" --region "$AWS_REGION"
    
    # Verificar si la inserción fue exitosa
    if [ $? -eq 0 ]; then
        echo "✅ Transacción insertada: ID=$TRANSACTION_ID, Amount=$AMOUNT, Currency=$CURRENCY, Method=$PAYMENT_METHOD, Status=$STATUS"
    else
        echo "❌ Error al insertar la transacción $TRANSACTION_ID y timestap $TIMESTAMP"
    fi

    # Esperar 0.1 segundos para evitar timestamps duplicados (opcional)
    sleep 0.1
done

echo "✅ Se han cargado 100 registros en la tabla '$TABLE_NAME'."
