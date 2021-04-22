import json
import time
import boto3
import os
#import input_data
import tarfile
import botocore
#import tensorflow as tf
import threading
import pickle
import redis
import numpy as np
from time import sleep
#from worker import train
import uuid
unique_id = uuid.uuid1()

#my_ip='34.229.200.194'
#redis_client = redis.Redis(host=my_ip, port=7000)
my_ips = ['3.235.242.221', '44.192.25.38', '3.235.175.83']#
ports = ["7000"]*len(my_ips)
clinets = []
#for port in ports:
for i in range(len(my_ips)):
    clinets.append(redis.Redis(host=my_ips[i], port=ports[i]))
r_connect = redis.Redis(host=my_ips[0], port=ports[0])

def parallel_read_shards(file_name, sharded_sgd):
    '''temp = []
    with open('/tmp/{}'.format(file_name), 'rb') as fp:
        temp = pickle.load(fp)
    os.remove('/tmp/{}'.format(file_name))
    sharded_sgd.append(np.array(temp))'''
    vals = redis_client.get(file_name)
    sharded_sgd.append(np.array(pickle.loads(vals)))
    
   
def upload_aggregated_sgd_shard(aggregator_id):
    BUCKET_NAME = 'bucket-sgd'#'s3-upload-pickle-test'
    s3_client = boto3.resource('s3')
    file_name = 'aggregated_shard_{}.pkl'.format(aggregator_id)
    s3_client.Bucket(BUCKET_NAME).upload_file('/tmp/{}'.format(file_name), file_name)

def download_sharded_sgd(total_clients, aggregator_id, num_shards):
    sharded_sgd = []
    BUCKET_NAME = 's3-upload-pickle-test'
    s3_client = boto3.resource('s3')
    
    #print(os.listdir('/tmp/'))
    threads = list()
    time_download = int(time.time()*1000)
    i = 0
    #for i in range(total_clients):
    while i < total_clients:
        file_name = 'worker_{}_grads_shard_{}.pkl'.format(i,aggregator_id)
        '''#dl_filename = 'worker_{}_grads_shard_{}.pkl'.format(i,aggregator_id)
        dl_filename =  os.path.join('{}_workerid_{}_shard'.format(i,aggregator_id), 'worker_{}_grads_shard_{}.pkl'.format(i,aggregator_id))
        #print('downloading  file {}'.format(file_name))
        try:
            s3_client.Bucket(BUCKET_NAME).download_file(dl_filename, '/tmp/{}'.format(file_name))
            i +=1
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                #print("shard {} does not exist yet in S3".format(file_name))
                sleep(0.1)
                continue
                #exit(1)'''
        #vals = redis_client.get(file_name)
        vals = clinets[i%len(my_ips)].get(file_name)#("sgd-worker-{}-shard-{}".format(i,aggregator_id))
        #sharded_sgd.append(np.array(pickle.loads(vals)))
        '''x = threading.Thread(target=parallel_read_shards, args=(file_name, sharded_sgd))
        threads.append(x)
        x.start()'''
        i +=1
        if i == total_clients:
            sharded_sgd = vals 
    
    #for thread in threads:
    #    thread.join()
    print("shard_download_time = {}".format(int(time.time()*1000) - time_download))
    #print(os.listdir('/tmp/'))
    time_upload = int(time.time()*1000)
    #temp = np.array(sharded_sgd)
    #avg_grads = temp.mean(axis=0)
    '''file_name = '/tmp/aggregated_shard_{}.pkl'.format(aggregator_id)
    with open(file_name, 'wb') as fp:
        pickle.dump(avg_grads, fp)
    upload_aggregated_sgd_shard(aggregator_id)'''
    file_name = 'aggregated_shard_{}.pkl'.format(aggregator_id)
    #redis_client.set(file_name,pickle.dumps(sharded_sgd))
    r_connect.set(file_name,pickle.dumps(sharded_sgd))
    print("Uploading the aggregated shard {}".format(file_name))
    print("aggregated_shard_upload_time = {}".format(int(time.time()*1000) - time_upload))
    

if __name__ == '__main__':
    download_sharded_sgd(1,0,1)

def lambda_handler(event, context):

    function_beign = int (time.time()*1000)
    print("Shard_aggregator_starting_Time = {}".format(function_beign))
    print("Manager_invocation_delay {}".format(function_beign - event["delay"]))
    print('Got asked to aggregate...')

    clientLambda = boto3.client('lambda')
    miniBatch_count = event["miniBatch_count"]
    epoch_count = event["epoch_count"] 
    total_clients = event["total_clients"]
    total_mini_batches = event["total_mini_batches"]
    aggregator_id = event["aggregator_id"]
    total_epochs = event["total_epochs"]
    round_time = event["round_time"]
    num_shards = event["num_shards"]
    
    buf = open('/proc/self/cgroup').read().split('\n')[-3].split('/')
    #vm_id, inst_id = buf[1], buf[2]
    #print ("Shard_aggregator{}\tvm_id\t{}\tinst_id\t{}\tu_id\t{}".format(aggregator_id, vm_id,inst_id, unique_id ))
    print ("Shard_aggregator{}\tu_id\t{}".format(aggregator_id, unique_id ))

    if aggregator_id < num_shards:
        download_sharded_sgd(total_clients,aggregator_id, num_shards)
    
    response = {"miniBatch_count":miniBatch_count, "total_clients":total_clients, 
                "epoch_count":epoch_count,"total_mini_batches":total_mini_batches,
            "total_epochs": total_epochs, "shard_aggregator_id":aggregator_id, "round_time":round_time,
             "num_shards": num_shards, "delay": int(time.time()*1000), "epoch_time":event["epoch_time"], "batch_size": event["batch_size"]} 
    
    print('Finished training and sent response..') #, response)
    print("Shard_aggregator_execution_time {}".format(int(time.time()*1000) - function_beign ))

    return response

if __name__ == '__main__':
    download_sharded_sgd(10, 0, 10)

