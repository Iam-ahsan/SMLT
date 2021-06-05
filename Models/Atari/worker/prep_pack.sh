#/bin/bash

cd ./Worker
ls
sudo docker  build -t lambda-tensorflow-example .
sudo docker tag lambda-tensorflow-example:latest 100676110906.dkr.ecr.us-east-1.amazonaws.com/lambda-tensorflow-example:latest
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 100676110906.dkr.ecr.us-east-1.amazonaws.com
sudo docker push 100676110906.dkr.ecr.us-east-1.amazonaws.com/lambda-tensorflow-example:latest
aws lambda update-function-code --region us-east-1 --function-name tensorflow-endpoint --image-uri 100676110906.dkr.ecr.us-east-1.amazonaws.com/lambda-tensorflow-example:latest
			

aws ecr get-login-password --region ${aws_region} \
        | docker login \
        --password-stdin \
        --username AWS \
        "${aws_account}.dkr.ecr.${aws_region}.amazonaws.com/${repository}									  
