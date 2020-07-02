#!/bin/bash

mkdir filestozip
python3 -m pip install -r /lambda/package-requirements.txt -t filestozip

# remove any old .zips
rm -f /io/deployment/lambda.zip

# copy required fonts
cp -r /io/assets/fonts filestozip

# copy lambda function
cp -r /io/awslambda/src/lambda_function.py filestozip
cp -r /io/awslambda/src/modules filestozip

# zip without any containing folder (or it won't work)
cd filestozip
mkdir /io/deployment
zip -r /io/deployment/lambda.zip * .[^.]*
