#!/bin/bash


#rm  mxnet_shard_aggregator.zip
#zip -9r mxnet_shard_aggregator.zip  * 
zip -g mxnet_shard_aggregator.zip lambda_function.py #grads.pkl #util.py
aws s3 rm s3://mystep-function-packages/mxnet_shard_aggregator.zip
aws s3 cp mxnet_shard_aggregator.zip s3://mystep-function-packages
echo "https://mystep-function-packages/redis-client.zip"
aws lambda update-function-code --function-name Mxnet_train_shard_aggregator --s3-bucket mystep-function-packages --s3-key mxnet_shard_aggregator.zip

##echo "workerTest"

