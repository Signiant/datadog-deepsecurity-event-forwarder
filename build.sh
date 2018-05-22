#!/bin/bash
BUCKET=$1
PROFILE=$2
REGION=$3

echo "Installing python modules"
cd lambda-src
pip install -r requirements.txt -t .
cd ..

echo "Running package step"
aws cloudformation package \
    --template-file template.yaml \
    --s3-bucket ${BUCKET} \
    --output-template-file packaged-template.yaml \
    --profile ${PROFILE}

echo "Running deploy step"
aws cloudformation deploy \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --template-file ./packaged-template.yaml \
    --stack-name trend-deep-security-events-to-datadog \
    --parameter-overrides EventFilter=all DatadogAPIKey=GLOBAL_DATADOG_APIKEY_CFN\
    --profile ${PROFILE} \
    --region ${REGION}
