import json
import time
import boto3
import os
import tarfile
import pickle
#import cifar10
import math
import botocore
import util
import numpy as np
#import tensorflow as tf
import uuid
unique_id = uuid.uuid1()

def get_gradients(filename, num_shards, worker_id):
    BUCKET_NAME = 'nlp-grads'
    s3_client = boto3.resource('s3')
    s3_client.Bucket(BUCKET_NAME).download_file(filename, '/tmp/{}'.format(filename))
    time_upload_pickle = int(time.time()*1000)
    my_flat_data = flat_data(filename)
    print("flat_sgd_time = {}".format(int(time.time()*1000) - time_upload_pickle))
    util.upload_data_s3(my_flat_data, num_shards, worker_id)
    print("upload_sharded_sgd_time = {}".format(int(time.time()*1000) - time_upload_pickle))

def flat_data(filename):
    data = []
    flat = []
    with open('/tmp/{}'.format(filename),'rb') as fp:
        data =pickle.load(fp)
    print(len(data))
    for val in data:
        if (len(np.shape(val)))!=0:
            flat.append(val)
    return flat

def lambda_handler(event, context):

    function_beign = int (time.time()*1000)
    print("Worker_starting_Time = {}".format(function_beign))
    print("Worker_invocation_delay {}".format(int(time.time()*1000) - event["delay"]))
    clientLambda = boto3.client('lambda')
    miniBatch_count = event["miniBatch_count"]
    epoch_count = event["epoch_count"] 
    total_workers = event["total_clients"]
    total_mini_batches = event["total_mini_batches"]
    worker_id = event["worker_id"]
    total_epochs = event["total_epochs"]
    round_time = event["round_time"]
    num_shards = event["num_shards"]
    batch_size = event["batch_size"]

    buf = open('/proc/self/cgroup').read().split('\n')[-3].split('/')
    
    print ("Worker_{}\tu_id\t{}".format(worker_id,unique_id ))

    time_get_trainingdata_s3 = int(time.time()*1000)
    util.download_trainingdata()
    print("time_get_trainingdata_s3  = {}".format(int(time.time()*1000) - time_get_trainingdata_s3))

    time_get_trainingindexes_s3 = int(time.time()*1000)
    if total_workers == 1 :
        training_indexes = [i for i in range(50000)]
        training_indexes = training_indexes[miniBatch_count*batch_size: min((miniBatch_count*batch_size)+batch_size, len(training_indexes))]        
    else:
        
        training_indexes = util.download_training_indexes(worker_id)
        training_indexes = training_indexes[miniBatch_count*batch_size: min(len(training_indexes),(miniBatch_count*batch_size)+batch_size)] 
        
    print("time_get_trainingindexes_s3 = {}".format(int(time.time()*1000) - time_get_trainingindexes_s3))

    miniBatch_count = int(math.ceil(50000.0/total_workers))
    #print(miniBatch_count)
    model = bert_medium.Train(worker_id,miniBatch_count, epoch_count+1, total_workers, training_indexes, num_shards)
    model.train_org()
    get_gradients('L12_grads.pkl', num_shards, worker_id) #L2_grads.pkl
    response = {"epoch_count":epoch_count,"miniBatch_count":miniBatch_count, "total_clients":total_workers,
                "total_mini_batches":total_mini_batches,"total_epochs": total_epochs, "aggregator_id":worker_id,
                "round_time":round_time, "num_shards": num_shards, "delay": int(time.time()*1000), 
                "epoch_time":event["epoch_time"], "batch_size":batch_size} 
    
    #util.remove_files("grads_shard")
    print("Worker_execution_time {}".format(int(time.time()*1000) - function_beign ))
    return response
if __name__=='__main__':
    get_gradients('new_L12_grads.pkl', 10, 2)

