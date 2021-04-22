import pickle
import json
import time
import boto3
import botocore
import math
import threading 
import os
import redis
import time
import numpy as np


my_ips = ['3.235.242.221', '44.192.25.38', '3.235.175.83']
ports = ["7000"]*len(my_ips)

#redis_client = redis.Redis(host=my_ip, port=7000)

def read_data(file_name):
        data = None
        with open("/tmp/{}".format(file_name), "rb") as fp:
            data = pickle.load(fp)
        #print(data.shape)
        return data

def remove_files(prefix):    
    filelist = os.listdir('/tmp/')
    #print(os.listdir('/tmp/'))
    for filename in filelist:
        if prefix not in filename:
            os.remove('/tmp/{}'.format(filename))

def download_training_indexes(worker_id):
    sharded_sgd = []
    BUCKET_NAME = 'index-training'
    s3_client = boto3.resource('s3')
    #print(os.listdir('/tmp/'))
    threads = list()
    time_download = int(time.time()*1000)
    filename = 'worker_{}_training_indices.pkl'.format(worker_id)
    status = False
    while status == False:
        try:
            s3_client.Bucket(BUCKET_NAME).download_file(filename, '/tmp/{}'.format(filename))
            indexes = []
            with open('/tmp/{}'.format(filename), 'rb') as fp:
                indexes = pickle.load(fp)
            os.remove('/tmp/{}'.format(filename))
            status = True
            return indexes
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("training indices {} do not exist in S3".format(filename))
                status = False
                #exit(1)

def generate_training_samples( train_data, train_labels, training_indexes): 
        dict_user_train = {}
        dict_user_train[0] = training_indexes
 
        my_train_data = train_data 
        my_final_data = my_train_data[dict_user_train[0]]

        my_train_label = train_labels 
        my_final_label = my_train_label[dict_user_train[0]]

        return my_final_data, my_final_label


def download_trainingdata():
    
    file_name = ['cifar10_train_x', 'cifar10_train_y']
    my_dir_set = set(os.listdir('/tmp'))
    if file_name[0] in my_dir_set:
        print("Images already exist")
        return True
    
    mys3_clinet = boto3.resource('s3')
    BUCKET_NAME = 'sagemaker-us-east-1-100676110906'

    for my_file in file_name:
        dwonload_path = os.path.join(os.sep, 'tmp', my_file)
        s3_path = os.path.join(
            'cifar10train_data','{}'.format(my_file))
        try:
            mys3_clinet.Bucket(BUCKET_NAME).download_file(
		                        s3_path,
		                        dwonload_path)
            
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("Training data does not exist")
                exit(1)
    return True

def upload_data_s3(flatten_sgd_vals, shards, workerid):
    threads = list()
    fsize = len(flatten_sgd_vals)/shards
        
    increment = int(math.ceil(len(flatten_sgd_vals) /float(shards)))
    client_config = botocore.config.Config(max_pool_connections=26,)
    s3 = boto3.resource('s3', config=client_config)
    BUCKET_NAME = 's3-upload-pickle-test'
    redis_client = redis.Redis(host=my_ips[workerid%len(my_ips)], port=ports[workerid%len(my_ips)])
    for i in range(shards): #shards
        filename = 'worker_{}_grads_shard_{}.pkl'.format(workerid,i)
        final_val =  min(len(flatten_sgd_vals), (i*increment)+increment)
        strating = i*increment
        redis_client.set(filename,pickle.dumps(flatten_sgd_vals[strating:final_val]))
        #x = threading.Thread(target= parallel_upload_data, args=(s3, BUCKET_NAME, filename, flatten_sgd_vals[strating:final_val], i, redis_client))
        #threads.append(x)
        #x.start()
    #for thread in threads:
    #    thread.join()

def parallel_upload_data(s3, BUCKET_NAME, filename, data, index, r_client):
    '''s3.Bucket(BUCKET_NAME).upload_file('/tmp/{}'.format(filename),filename)
    os.remove('/tmp/{}'.format(filename))'''
    #with open("./tmp/sgd_shard_{}.pkl".format(index), 'wb') as fp:
    #    pickle.dump(data, fp)
    #print("I am here")
    r_client.set(filename,pickle.dumps(data))

def flatten_sgd(grad_val):
    flatten_sgd_vals = []
    concat = [1]*18
    do_it = [False]*18
    concat[12], concat[14] = 512, 1024
    do_it[12], do_it[14] = True, True
    for i in range(len(grad_val)):
        if do_it[i]:
            for j in range(concat[i]):
                flatten_sgd_vals.extend([grad_val[i][j]])
        else:
            flatten_sgd_vals.extend([grad_val[i]])
    return flatten_sgd_vals

def if_chkpt_exists():
    time_download_checkpoint = int(time.time()*1000)
    mys3_clinet = boto3.resource('s3')
    BUCKET_NAME = 'sagemaker-us-east-1-100676110906'
    print("checking the checkpoint")
    filename = ["model.index", "model.data-00000-of-00001","checkpoint"]
    for name in filename:
        #print("checking the file {}".format(name))
        CHKPT_PATH = os.path.join(os.sep, 'tmp', name)
        CHKP_FILENAME = os.path.join(
            'checkpoint','{}'.format(name))
        
        try:
            mys3_clinet.Bucket(BUCKET_NAME).download_file(
                                CHKP_FILENAME,
                                CHKPT_PATH)
                
        except botocore.exceptions.ClientError as e:
            print(e.response['Error']['Code'])
            if e.response['Error']['Code'] == "404" or e.response['Error']['Code'] == "403" :
                print("CHKPT dose not exist")
                return False
    print("Checkpoint_download_load_time = {}".format(int(time.time()*1000) - time_download_checkpoint))        
    return True

def upload_minibatch_sgd(filename):
    s3 = boto3.resource('s3')
    BUCKET_NAME = 'bucket-sgd'
    start_time = int(time.time()*1000)
    s3.Bucket(BUCKET_NAME).upload_file('/tmp/{}'.format(filename),filename)
    latency = int(time.time()*1000) - start_time
    rm_file = '/tmp/{}'.format(filename)
    os.remove(rm_file)

def upload_chkpt():
    #remove_cp_s3_file()
    time_upload_checkpoint = int(time.time()*1000)
    s3 = boto3.resource('s3')
    BUCKET_NAME = 'sagemaker-us-east-1-100676110906'
    filename = ["model.index", "model.data-00000-of-00001","checkpoint"]
    for name in filename:
        CHKP_FILENAME = os.path.join(
            'checkpoint',name)
        start_time = int(time.time()*1000)
        s3.Bucket(BUCKET_NAME).upload_file('/tmp/{}'.format(name),CHKP_FILENAME)
        latency = int(time.time()*1000) - start_time
        #print(latency)
        #sleep(2)
        rm_file = '/tmp/{}'.format(name)
        os.remove(rm_file)
    l = os.listdir('/tmp/')
    for i in range(len(l)):
        if "grads" in l[i]:
            os.remove('/tmp/{}'.format(l[i]))
    print("Checkpoint_upload_load_time = {}".format(int(time.time()*1000) - time_upload_checkpoint))

def write_client_responses(my_id):
    s3 = boto3.resource('s3')
    BUCKET_NAME = 'bucket-sgd'#'aali173-deeplearning-test-bucket'
    s3.Object(BUCKET_NAME, 'grads-{}.pkl'.format(my_id)).put(Body=json.dumps(my_id))
    #print('uploded grads file', 'grads-{}.pkl'.format(my_id), 'to s3')
