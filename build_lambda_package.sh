#!/bin/bash

set -e

echo "🧼 Limpiando entorno anterior..."
rm -rf build lambda_package.zip
mkdir -p build/python

echo "📦 Instalando dependencias desde requirements.txt..."
pip install -r lambda/requirements.txt -t build/python \
  --no-cache-dir --only-binary=:all:

echo "🧹 Eliminando archivos innecesarios..."
find build/python -type d -name '__pycache__' -exec rm -rf {} +
find build/python -type d -name 'tests' -exec rm -rf {} +
find build/python -type d -name '*.dist-info' -exec rm -rf {} +
find build/python -type f -name '*.pyc' -delete

echo "📁 Copiando código fuente..."
cp -r lambda/extractor build/python/
cp -r lambda/transformer build/python/
cp -r lambda/parser build/python/

echo "🗜️ Comprimiendo en lambda_package.zip..."
cd build/python
zip -r ../../lambda_package.zip .
cd ../../..

echo "✅ Paquete generado: lambda_package.zip"
du -sh lambda_package.zip
