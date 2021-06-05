#!/bin/bash


rm  simulation_global-aggregator.zip
cp ../redis-numpy-p37.zip ./simulation_global-aggregator.zip
zip -g simulation_global-aggregator.zip aggregator_main.py util.py
#aws s3 rm s3://mystep-function-packages/simulation_global-aggregator.zip
aws s3 cp simulation_global-aggregator.zip s3://mystep-function-packages
echo "https://mystep-function-packages/stepfunction-global-aggregator-bundle.zip"
aws lambda update-function-code --function-name simulation_global-aggregator --s3-bucket mystep-function-packages --s3-key simulation_global-aggregator.zip
echo "workerTest"

