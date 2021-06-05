# SMLT 


This is the repository of Serverless Machine Learning Training (SMLT) Framework

## SMLT Overview
<img align="center" src=https://github.com/Iam-ahsan/SMLT/blob/main/overview.png>
The above Figure summarizes the SMLT framework, describing the interactions between different modules during the training process. To start a training process, users provide the ML model, training data and training code which are uploaded to the object store, as well as their performance and budget requirements. First, the **Artifact manager** uploads the user-provided training code and data to cloud *Object Store* (1). Next, the **Task Scheduler** starts the training process with initial (arbitrary) training resources (i.e., worker memory allocation and the number of workers) (2). As soon as the workers are deployed by the cloud provider, the **Data Iterator** in each worker  downloads the assigned training data and code (3). Then, in (4), the **Minibatch Buffer** loads the training data to memory from the local storage, after which the **Trainer** initiates the  training process (5). Upon the completion of a single iteration,  the generated model parameters are provided as input to the [Hierarchical Aggregator](https://github.com/Iam-ahsan/SMLT#hierarchical-aggregator) (6) explained in , which is responsible for updating the model parameters using the mechanism described below (7). While the hierarchical aggregator updates the model parameters, the **Resource Manger** in the end client also reads the parameter metadata from the parameter store to check the health of each training worker (7b). Failure of any worker is detected through a missing key in the metadata after each iteration. Afterwards, the **Task Scheduler** collects the training performance (i.e., throughput) as well as the training status (i.e., current batch size, learning rate, epoch count, etc.) (8). The **Task Scheduler** also restarts any failed workers as necessary. The training performance and status are further utilized by the **Resource Manager** to optimize the training performance using Bayesian optimization (9). Finally, the updated training resources are shared with the **Task Scheduler** (10), and the process continues until a certain number of epochs or the desired accuracy is achieved.

## Hierarchical Aggregator 
<img aligh=center src=https://github.com/Iam-ahsan/SMLT/blob/main/Shard%20Aggregator.png>
Our mechanism performs the synchronization of gradients generated by all workers in a MapReduce-alike fashion among the workers themselves. Specifically, after each iteration, our hierarchical synchronization mechanism takes the model gradients generated by each worker as input.  The **shard generator** module,  residing in each of the **n** workers, divides the input gradients into **m** equal-sized shards (1). These shards are uploaded to the **parameter store**  which acts as a communication intermediary between the stateless serverless workers (2). 
In SMLT, each serverless worker also acts as a shard aggregator (thus, **n** equals **m**, but they could also be different).
The sharded gradients are further downloaded by the **shard aggregator** module  residing in each worker (3).  Each shard aggregator is responsible for aggregating a particular shard generated by all workers. For example, the 'shard aggregator 1' in above figure is responsible for aggregating the first shard from all workers to perform a mean operation. We call the resulting value as **aggregated shard**, which is again uploaded to the parameter store  by each shard aggregator (4). After this step, the parameter store contains the updated parameters of all workers in a sharded form. Finally, the **global ggregator** module residing in each worker downloads all the aggregated shards, and reconstructs the updated model for the next iteration (5).

---
## Prerequisite
- [AWS  Cli](https://aws.amazon.com/cli/)
- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Bayesian Optimization](https://github.com/fmfn/BayesianOptimization)
- [Redis](https://pypi.org/project/redis-server/)

## Evaluation Platform
 We prototype SMLT atop AWS lambda and performed the verification and validation studies using Tensorflow, Pytorch and MxNet. We use the following ML models for our evaluation studies. 
  1. ResNet-18 (with 18 layers, 11 million parameters) and ResNet-50 (with 50 layers, 23 million parameters) ~\cite{he2016deep} are medium size image classification models with residual functions.
  2. Bert-Small (with 66 million parameters), Bert-Medium (with 110 milion parameters) and Bert-Medium (with 340 milion parameters) are state-of-the-art NLP models.
  3. We use Reinforcement learning to train Atari break out game with a total of 50 million frames.
### Object Store
 We use S3 as our object store. To upload the training code and the training data the artifact manager takes the function name, artifact name and the bucket name as an input. 
 ### Parameter Store
 We use Redis version 6.2.1 as our parameter store. Users can either host the parameter store on an EC2 instaces or AWS fargate for hosting the paramter store. In our evaluation setup we hosted our parameter store on AWS fargate with instance type C5.4xlare. Once the parameter store is setup the ip address of the parameter store is updated in the respective modules (Shard generator, shard aggregator and global aggregator)
 ## Deployment
 To deploy the Lambda serverless function follow the instruction in the this [tutorial](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-package.html#gettingstarted-package-awsother)
 
 ## Run Experiments
 ### Artifact Manager
 Must be run with bash. Pleace the "Artifact Manager.sh" in the folder containing the training code and the respective dependencies. Artifact manager takes the following parameter as input.
   1. Function Name (https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html)
   2. Bucket Name (https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html)
   3. Package Name (https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-package.html#gettingstarted-package-awsother)
   4. AWS Role (https://aws.amazon.com/premiumsupport/knowledge-center/lambda-execution-role-s3-bucket/)
 
 To run the Artifact Manager, try: ./Artifact-Manager.sh $Function-Name $Bucket Name $Package Name $AWS Role. Sample code for various models are available in the Model directory. Due to space limitation of githun we were unbale to add all the dependencies for the examples.
 ### Training Scheduler
 Must be run with python3 and requires the following modules:
  1. Boto3 (https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
 Training Manager takes the following parameter as input.
  1. Global batch size
  2. Number of training workers
  3. Number of training epochs
  Once the model artifact is deployed and the function are created training scheduler is used for initiating the training process. 
  To run the training scheduler, try: python training-schaduler.py global-batch-size number-of-worker number-of-epochs
  
 ### Performance Optimizer
After every epcoh the training scheduler collectes the performacne metrics from the training workers such as training time and communication time. this information is furhter utilized by the performance optimizer to improve the training speed or user specified threadhold (cost of training time). The performacne optimizer is based on Bayesian Optimization.
