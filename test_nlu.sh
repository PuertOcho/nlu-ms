#!/bin/bash

echo "🚀 Iniciando servicio NLU de Puerto Ocho..."

# Levantar el servicio
docker run -d --name puertocho-nlu-test -p 5001:5001 \
  -v $(pwd)/server:/root/server \
  puertocho-nlu:latest

echo "⏳ Esperando que el servicio esté listo..."
sleep 20

# Verificar que el servicio esté corriendo
if curl -s http://localhost:5001/health >/dev/null; then
    echo "✅ Servicio NLU está funcionando"
else
    echo "❌ Error: El servicio no está respondiendo"
    exit 1
fi

echo "🎯 Entrenando modelo en español..."
curl -X POST "http://localhost:5001/train?domain=hogar&locale=es"

echo -e "\n⏳ Esperando que termine el entrenamiento..."
sleep 60

echo -e "\n🧪 Probando predicciones..."

echo "Prueba 1: 'enciende la luz de la cocina'"
curl -X POST "http://localhost:5001/predict?domain=hogar&locale=es&userUtterance=enciende%20la%20luz%20de%20la%20cocina"

echo -e "\n\nPrueba 2: 'qué hora es'"
curl -X POST "http://localhost:5001/predict?domain=hogar&locale=es&userUtterance=qué%20hora%20es"

echo -e "\n\nPrueba 3: 'reproduce música'"
curl -X POST "http://localhost:5001/predict?domain=hogar&locale=es&userUtterance=reproduce%20música"

echo -e "\n\n🧹 Limpiando contenedor de prueba..."
docker stop puertocho-nlu-test
docker rm puertocho-nlu-test

echo "✅ Pruebas completadas" 