# SMLT 


This is the repository of Serverless Machine Learning Training (SMLT) Framework

# SMLT ![Overview](img align="center" src=https://github.com/Iam-ahsan/SMLT/blob/main/figures/overview.png)
<img align="center" src=https://github.com/Iam-ahsan/SMLT/blob/main/figures/overview.png>
The above Figure summarizes the SMLT framework, describing the interactions between different modules during the training process. To start a training process, users provide the ML model, training data and training code which are uploaded to the object store, as well as their performance and budget requirements. First, the **Artifact manager** uploads the user-provided training code and data to cloud **Object Store** \circledWhite{1}. Next, the **Task Scheduler** starts the training process with initial (arbitrary) training resources (i.e., worker memory allocation and the number of workers) \circledWhite{2}. As soon as the workers are deployed by the cloud provider, the **Data Iterator** in each worker  downloads the assigned training data and code \circledWhite{3}. Then, in \circledWhite{4}, the **Minibatch Buffer** loads the training data to memory from the local storage, after which the **Trainer** initiates the  training process \circledWhite{5}. Upon the completion of a single iteration,  the generated model parameters are provided as input to the **Hierarchical Aggregator** \circledWhite{6}, which is responsible for updating the model parameters using the mechanism described in Section \ref{sec:modelsync} \circledWhite{7a}. While the hierarchical aggregator updates the model parameters, the **Resource Manger** in the end client also reads the parameter metadata from the parameter store to check the health of each training worker \circledWhite{7b}. Failure of any worker is detected through a missing key in the metadata after each iteration. Afterwards, the **Task Scheduler** collects the training performance (i.e., throughput) as well as the training status (i.e., current batch size, learning rate, epoch count, etc.) \circledWhite{8}. The **Task Scheduler** also restarts any failed workers as necessary. The training performance and status are further utilized by the **Resource Manager** to optimize the training performance using Bayesian optimization \circledWhite{9}. Finally, the updated training resources are shared with the **Task Scheduler** \circledWhite{10}, and the process continues until a certain number of epochs or the desired accuracy is achieved.

# Hierarchical Aggregator ![Hierarchical Aggregator](https://github.com/Iam-ahsan/SMLT/blob/main/figures/Shard%20Aggregator.png)
<img aligh=center src=https://github.com/Iam-ahsan/SMLT/blob/main/figures/Shard%20Aggregator.png>
---
**prerequisite**
- [AWS  Cli](https://aws.amazon.com/cli/)
- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
