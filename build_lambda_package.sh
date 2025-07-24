#!/usr/bin/env bash
set -e
echo "🔄  Rebuilding Lambda package..."
rm -rf build lambda_package.zip
mkdir build
pip install -r ./lambda/requirements_extractor.txt --target build/
cp -r ./lambda/extractor/ build/
(cd build && zip -r ../lambda_package.zip .)
echo "✅  lambda_package.zip listo"
