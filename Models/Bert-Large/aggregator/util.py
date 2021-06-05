import pickle
import json
import time
import boto3
import botocore
import math
import threading 
import redis
import os
import time
import numpy as np
import redis
from time import sleep
my_ip='34.229.200.194'
redis_client = redis.Redis(host=my_ip, port=7000)

def generate_training_index(numworkers):
    if numworkers < 4:
        numworkers = 10
    train_samples = 50000
    train_item_per_worker = int (train_samples//numworkers)
    dict_user_train = {}
    train_idx = [i for i in range(train_samples)]
    for i in range(numworkers):
        dict_user_train[i] = np.random.choice(train_idx, train_item_per_worker)
    return dict_user_train

def upload_training_index(training_indexs, total_workers):  
    client_config = botocore.config.Config(max_pool_connections=total_workers,)
    s3 = boto3.resource('s3', config=client_config)
    bucket_name = 'index-training'
    threads = list()
    for i in range(total_workers): #shards
        filename = 'worker_{}_training_indices.pkl'.format(i)
        # for parallel uploads
        x = threading.Thread(target=parallel_upload_training_index, args=(s3, bucket_name, filename, 
            training_indexs[i].tolist()))
        threads.append(x)
        x.start()
    for thread in threads:
        thread.join()

def parallel_upload_training_index(s3, bucket_name, filename, data):
    with open('/tmp/{}'.format(filename), 'wb') as fp:
            pickle.dump(data, fp)
    s3.Bucket(bucket_name).upload_file('/tmp/{}'.format(filename),filename)
    rm_file = '/tmp/{}'.format(filename)
    os.remove(rm_file)

def download_aggregated_sharded_sgd(shards,grads_placeholder):
    sharded_sgd = []
    bucket_name = 'bucket-sgd' 
    s3_client = boto3.resource('s3')
    threads = list()
    i = 0
    while i < shards:
        file_name = 'aggregated_shard_{}.pkl'.format(i)
        vals = redis_client.get(file_name)
        temp = np.array(pickle.loads(vals))
        sharded_sgd.extend(temp)
        #print(len(sharded_sgd))
        i += 1
        '''try:
            s3_client.Bucket(bucket_name).download_file(file_name, '/tmp/{}'.format(file_name))
            i += 1
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("Aggregated shard {} does not exist yet".format(file_name))
                sleep(0.1)
                continue

        x = threading.Thread(target=parallel_read_shards, args=(file_name, sharded_sgd, grads_placeholder))
        threads.append(x)
        x.start()'''
    
    '''for thread in threads:
        thread.join()'''
    final = reconstruct(sharded_sgd, grads_placeholder)
    return final

def parallel_read_shards(file_name, sharded_sgd, grads_placeholder):
    temp = []
    with open('/tmp/{}'.format(file_name), 'rb') as fp:
        temp = pickle.load(fp)
    os.remove('/tmp/{}'.format(file_name))
    sharded_sgd.extend(temp)

def reconstruct(sharded_sgd, grads_placeholder):
    concat =[1]*18 # [784, 1, 1200, 1,1,1]
    do_it = [False]*18
    concat[12], concat[14] = 512, 1024
    do_it[12], do_it [14] = True, True
    start = 0
    final = []
    feed_dict = {}
    for i in range(len(concat)):
        if do_it[i]:
            final.extend([sharded_sgd[start: start + concat[i]]])
        else:
            final.extend(sharded_sgd[start: start + concat[i]])
        start += concat[i]
    for i in range(len(grads_placeholder)):
        #print(np.shape(final[i]))
        feed_dict[grads_placeholder[i][0]] = final[i]
    return feed_dict


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
def write_client_responses(worker_id):
    s3 = boto3.resource('s3')
    bucket_name = 'sagemaker-us-east-1-100676110906'
    file = os.path.join('worker_updates','worker-{}.txt'.format(worker_id))
    s3.Object(bucket_name, file ).put(Body=json.dumps(worker_id))

'''def write_client_responses(my_id):
    s3 = boto3.resource('s3')
    BUCKET_NAME = 'bucket-sgd'#'aali173-deeplearning-test-bucket'
    s3.Object(BUCKET_NAME, 'grads-{}.pkl'.format(my_id)).put(Body=json.dumps(my_id))
    #print('uploded grads file', 'grads-{}.pkl'.format(my_id), 'to s3')'''


def remove_client_response_files_s3():
    s31 = boto3.resource('s3')
    bucket_name = 'sagemaker-us-east-1-100676110906'
    bucket = s31.Bucket(bucket_name)
    bucket.objects.filter(Prefix="worker_updates").delete()

def read_num_client_updates():
    my_Data = 0
    s3 = boto3.client('s3')
    bucket_name='sagemaker-us-east-1-100676110906'
    response = s3.list_objects(Bucket=bucket_name, Prefix='worker_updates') 
    my_Data = len(response['Contents'])
    return my_Data

def upload_chkpt():
    #remove_cp_s3_file()
    time_upload_checkpoint = int(time.time()*1000)
    s3 = boto3.resource('s3')
    bucket_name = 'sagemaker-us-east-1-100676110906'
    filename = ["model.index", "model.data-00000-of-00001","checkpoint"]
    for name in filename:
        CHKP_FILENAME = os.path.join(
            'checkpoint',name)
        start_time = int(time.time()*1000)
        s3.Bucket(bucket_name).upload_file('/tmp/{}'.format(name),CHKP_FILENAME)
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


#worker functions
def download_training_indexes(worker_id):
    sharded_sgd = []
    bucket_name = 'index-training'
    s3_client = boto3.resource('s3')
    #print(os.listdir('/tmp/'))
    threads = list()
    time_download = int(time.time()*1000)
    filename = 'worker_{}_training_indices.pkl'.format(worker_id)
    status = False
    while status == False:
        try:
            s3_client.Bucket(bucket_name).download_file(filename, '/tmp/{}'.format(filename))
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

def remove_bucketfile(bucketname):
    s3 = boto3.client('s3')
    s31 = boto3.resource('s3')
    print("deleting the files from s3")
    response = s3.list_objects(Bucket=bucketname) #(Bucket=BUKCET_NAME2)
    #print(response)
    if 'Contents' not in response.keys(): return 
    for i in range(len(response['Contents'])):
        #print("The file is being deleted {}".format(response["Contents"][i]['Key']))
        s31.Object(bucketname, response["Contents"][i]['Key']).delete()

def download_training_or_test_data(file_list):
    
    my_dir_set = set(os.listdir('/tmp'))
    if file_list[0] in my_dir_set:
        print("Images already exist")
        return True
    
    mys3_clinet = boto3.resource('s3')
    bucket_name = 'sagemaker-us-east-1-100676110906'

    for my_file in file_list:
        dwonload_path = os.path.join(os.sep, 'tmp', my_file)
        s3_path = os.path.join(
            'cifar10train_data','{}'.format(my_file))
        try:
            mys3_clinet.Bucket(bucket_name).download_file(
		                        s3_path,
		                        dwonload_path)
            
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("Training data does not exist")
                exit(1)
    return True

def upload_minibatch_sgd(filename):
    s3 = boto3.resource('s3')
    bucket_name = 'bucket-sgd'
    start_time = int(time.time()*1000)
    s3.Bucket(bucket_name).upload_file('/tmp/{}'.format(filename),filename)
    latency = int(time.time()*1000) - start_time
    rm_file = '/tmp/{}'.format(filename)
    os.remove(rm_file)


def upload_data_s3(flatten_sgd_vals, shards, workerid):
    threads = list()
    fsize = len(flatten_sgd_vals)/shards
        
    increment = int(math.ceil(len(flatten_sgd_vals) /float(shards)))
    client_config = botocore.config.Config(max_pool_connections=26,)
    s3 = boto3.resource('s3', config=client_config)
    bucket_name = 's3-upload-pickle-test'

    for i in range(shards): #shards
        filename = 'worker_{}_grads_shard_{}.pkl'.format(workerid,i)
        final_val =  min(len(flatten_sgd_vals), (i*increment)+increment)
        strating = i*increment
        x = threading.Thread(target= parallel_upload_data, args=(s3, bucket_name, filename, flatten_sgd_vals[strating:final_val], i))
        threads.append(x)
        x.start()
    for thread in threads:
        thread.join()

def parallel_upload_data(s3, bucket_name, filename, data, index):
    mutex_lock = threading.Lock()
    mutex_lock.acquire()
    with open('/tmp/{}'.format(filename), 'wb') as fp:
        pickle.dump(data, fp)
    mutex_lock.release()

    s3.Bucket(bucket_name).upload_file('/tmp/{}'.format(filename),filename)

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
    bucket_name = 'sagemaker-us-east-1-100676110906'
    print("checking the checkpoint")
    filename = ["model.index", "model.data-00000-of-00001","checkpoint"]
    for name in filename:
        print("checking the file {}".format(name))
        CHKPT_PATH = os.path.join(os.sep, 'tmp', name)
        CHKP_FILENAME = os.path.join(
            'checkpoint','{}'.format(name))
        
        try:
            mys3_clinet.Bucket(bucket_name).download_file(
                                CHKP_FILENAME,
                                CHKPT_PATH)
                
        except botocore.exceptions.ClientError as e:
            print(e.response['Error']['Code'])
            if e.response['Error']['Code'] == "404" or e.response['Error']['Code'] == "403" :
                print("CHKPT dose not exist")
                return False
    print("Checkpoint_download_load_time = {}".format(int(time.time()*1000) - time_download_checkpoint))        
    return True

def remove_chkpt():
    filename = ["mnist-fc-0.meta", "mnist-fc-0.index", "mnist-fc-0.data-00000-of-00001","checkpoint"]
    file_list = os.listdir('/tmp/')
    for name in filename:
       if name in file_list:
           rm_file = '/tmp/{}'.format(name)
           os.remove(rm_file)



if __name__ == "__main__":
    
    download_aggregated_sharded_sgd(100,{})
