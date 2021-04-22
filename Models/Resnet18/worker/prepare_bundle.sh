#!/bin/bash


rm  lambda_function_mxnet_train.zip
zip -9r lambda_function_mxnet_train.zip  *   
aws s3 rm s3://mystep-function-packages/lambda_function_mxnet_train.zip
aws s3 cp lambda_function_mxnet_train.zip s3://mystep-function-packages/lambda_function_mxnet_train.zip
aws lambda update-function-code --function-name Mxnet_train --s3-bucket mystep-function-packages --s3-key lambda_function_mxnet_train.zip
echo "workerTest"

