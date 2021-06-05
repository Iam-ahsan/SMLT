#!/bin/bash


rm  simulation_shard-aggregator.zip
cp ../redis-numpy-p37.zip ./simulation_shard-aggregator.zip
zip -g simulation_shard-aggregator.zip shard-aggregator.py
aws s3 rm s3://mystep-function-packages/simulation_shard-aggregator.zip
aws s3 cp simulation_shard-aggregator.zip s3://mystep-function-packages/
echo "https://mystep-function-packages.s3.amazonaws.com/stepfunction-sharded-aggregator-bundle.zip"
aws lambda update-function-code --function-name simulation_shard-aggregator --s3-bucket mystep-function-packages --s3-key simulation_shard-aggregator.zip
echo "sharded-aggregator"
