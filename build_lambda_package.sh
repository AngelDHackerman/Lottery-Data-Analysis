#!/usr/bin/env bash
set -e
echo "🔄  Rebuilding Lambda package..."
rm -rf build lambda_package.zip
mkdir build
pip install -r requirements.txt --target build/
cp -r extractor/ build/
(cd build && zip -r ../lambda_package.zip .)
echo "✅  lambda_package.zip listo"
