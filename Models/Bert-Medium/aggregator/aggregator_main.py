#from ResNet import ResNet
import json
import boto3
import botocore
import time
import os
import numpy as np
import threading 
import pickle
import redis
import util
from time import sleep
import uuid
unique_id = uuid.uuid1()

BUCKET_NAME = 'sagemaker-us-east-1-100676110906'
BUKCET_NAME2 = 'bucket-sgd' #'aali173-deeplearning-test-bucket'
mys3_clinet = boto3.resource('s3')
CHKPT_PATH = os.path.join(os.sep, 'tmp', 'mnist_chkpt')
CHKP_FILENAME = os.path.join(
    'checkpoint','checkpoint')

my_ip='3.235.242.221'
redis_client = redis.Redis(host=my_ip, port=7000)

def launch_workers(event):
    clientLambda = boto3.client('lambda')
    my_data_dist = {}
    my_data_dist = util.generate_training_index(event["total_clients"])
    training = "Not done"

    if event["epoch_count"] == 0 and event["miniBatch_count"] ==0:
        util.upload_training_index(my_data_dist, event["total_clients"])
    if event["epoch_count"] == event["total_epochs"] -1:
        training = "Done"

    mypacket = {"data":[],"training":training}
    round_time = time.time()
    for i in range (event["total_clients"]):
        response = {"miniBatch_count":event["miniBatch_count"], "epoch_count": event["epoch_count"],
            "total_clients":event["total_clients"], "total_mini_batches":event["total_mini_batches"], 
            "worker_id":i, "total_epochs":event["total_epochs"] , "round_time":round_time, "num_shards" : 
            event["num_shards"], "delay": int(time.time()*1000), "epoch_time":event["epoch_time"], 
            "batch_size":event["batch_size"]} #, "training_data": my_data_dist[i].tolist()
        mypacket["data"].append(response)    
    return mypacket

def download_aggregated_sharded_simulation(shards):
    
    sharded_sgd = []
    bucket_name = 'bucket-sgd' 
    s3_client = boto3.resource('s3')
    threads = list()
    i = 0
    while i < shards:
        file_name = 'aggregated_shard_{}.pkl'.format(i)
        vals = redis_client.get(file_name)
        temp = np.array(pickle.loads(vals))
        #print(len(sharded_sgd))
        i += 1

    return


def lambda_handler(event, context):
    # TODO implement
    function_beign = int (time.time()*1000)
    print("Aggregator_starting_Time = {}".format(function_beign))
    print("Aggregator_invocation_delay {}".format(function_beign - event[0]["delay"]))
    print("Round time = {}".format(time.time() - event[0]["round_time"]))
    event[0]["epoch_time"] += time.time() - event[0]["round_time"]

    buf = open('/proc/self/cgroup').read().split('\n')[-3].split('/')
    #vm_id, inst_id = buf[1], buf[2]
    #print ("Aggregator_instance_{}\tvm_id\t{}\tinst_id\t{}\tu_it\t{}".format(0,vm_id,inst_id,unique_id ))
    print ("Aggregator_instance_{}\tu_it\t{}".format(0,unique_id ))

    miniBatch_count = event[0]["miniBatch_count"] + 1
    epoch_count = event[0]["epoch_count"]
    total_epochs = event[0]["total_epochs"]
    total_workers = event[0]["total_clients"]
    total_mini_batches = event[0]["total_mini_batches"]
    round_time = event[0]["round_time"]
    shard_aggregator_id = event[0]["shard_aggregator_id"]
    num_shards = event[0]["num_shards"]
    batch_size = int(event[0]["batch_size"])

    #event[0]["total_mini_batches"] = int (50000/(batch_size*total_workers))
    event[0]["miniBatch_count"] += 1
    print("Training Epoch {} current minibatch {} out of Total {}".format(event[0]["epoch_count"],event[0]["miniBatch_count"], event[0]["total_mini_batches"]))

    if event[0]["miniBatch_count"] == event[0]["total_mini_batches"]:
        print("Total_Epoch_time = {}".format(event[0]["epoch_time"]))
        event[0]["epoch_time"] = 0
        event[0]["epoch_count"] += 1
        event[0]["miniBatch_count"] = 0

    time_get_testingdata_s3 = int(time.time()*1000)
    util.download_training_or_test_data(['cifar10_test_x', 'cifar10_test_y'])
    print("time_get_testingdata_s3  = {}".format(int(time.time()*1000) - time_get_testingdata_s3))
    if (event[0]["epoch_count"] > 0 or  event[0]["miniBatch_count"] > 0):    
        time_download = int(time.time()*1000)
        download_aggregated_sharded_simulation(num_shards)
        print("aggregated_shard_download_time = {}".format(int(time.time()*1000) - time_download))
    
    #cnn = cifar10.Train(event[0]["miniBatch_count"] , event[0]["epoch_count"], total_workers, event[0]["total_mini_batches"],num_shards, int(event[0]["batch_size"]))
    #cnn.train_org()

    '''if event[0]["epoch_count"] >= 0 or event[0]["miniBatch_count"] > 0:
        time_remove_shards_sgd_s3 = int(time.time()*1000)
        util.remove_bucketfile('bucket-sgd')
        print("time_remove_shards_sgd_s3  = {}".format(int(time.time()*1000) - time_remove_shards_sgd_s3 ))'''
    my_data = launch_workers(event[0])
    print("Execution time {}".format(int(time.time()*1000) - function_beign ))
    return my_data


    
if __name__=="__main__":
    #cnn = cifar10.Train()
    #cnn.train_org()
    with tf.Session() as sess: #config=tf.ConfigProto(allow_soft_placement=True)
        cnn = ResNet(sess, 0, 0) #, args
        # build graph
        cnn.build_model()
        cnn.train()
   
