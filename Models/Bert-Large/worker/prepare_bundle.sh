#!/bin/bash


rm  simulation_worker.zip
cp ../redis-numpy-p37.zip ./simulation_worker.zip
zip -g simulation_worker.zip  workermain.py util.py
aws s3 rm s3://mystep-function-packages/simulation_worker.zip
aws s3 cp simulation_worker.zip s3://mystep-function-packages/
echo "https://mystep-function-packages/redis-client.zip"
aws lambda update-function-code --function-name  simulation_worker --s3-bucket mystep-function-packages --s3-key simulation_worker.zip

echo "workerTest"
