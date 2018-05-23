#!/bin/bash -x
BUCKET=$1
PROFILE=$2
SSM_PARAM_STORE_API_KEY=$3
SSM_PARAM_STORE_APP_KEY=$4
DATADOG_TAGS=$5
REGION=$6


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
    --parameter-overrides EventFilter=all DatadogAPIKey=${SSM_PARAM_STORE_API_KEY} DatadogAppKey=${SSM_PARAM_STORE_APP_KEY} DatadogTags="${DATADOG_TAGS}"\
    --profile ${PROFILE} \
    --region ${REGION}
