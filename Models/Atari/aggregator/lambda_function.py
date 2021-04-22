import redis
import time
import pickle
import sys
import threading
import math
import numpy as np
import threading 

my_ips = ['3.235.242.221']#, '44.192.25.38', '3.235.175.83']#['34.229.200.194']
ports = ["7000"]*len(my_ips)
#ip ="3.236.145.167"
#r_connect = redis.Redis(host=ip, port=7006)
r_connect = redis.Redis(host=my_ips[0], port=ports[0])

def get_data(worker_id,shard_id):
   #r_connect = redis.Redis(host=ip, port=6379)
   vals = r_connect.get("sgd_worker_{}_shard_{}.pkl".format(worker_id,shard_id))
   return vals


def put_data(data, worker_id, shard_id):
    r_connect.set("aggregated_shard_{}".format(shard_id),pickle.dumps(data))
    
def paralle_read(val, s_id):
    print("I am here {}".format(s_id))
    data = pickle.loads(val)
    
def dl_sharded(worker_id, total_workers):
    i = 0
    threads = list()   
    while i < total_workers:
        read_data = get_data(worker_id, i)    
        i += 1
        x = threading.Thread(target= paralle_read, args=(read_data,i))
        x.start()
        threads.append(x)
        
    for thread in threads:
        thread.join()


def ul_agg_shard(worker_id,data):
    r_connect.set("aggregated_shard_{}".format(worker_id),pickle.dumps(data))




def dl_all(num_shards):
    i = 0
    threads = list()   
    while i < num_shards:
        r_connect.get("aggregated_shard_{}".format(i))
        '''read_data = r_connect.get("aggregated_shard_{}".format(i))
        x = threading.Thread(target= paralle_read, args=(read_data,i))
        threads.append(x)
        x.start()'''
        i += 1
    #for thread in threads:
    #    thread.join()

def launch_workers(event):
    training = "Not done"
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

def lambda_handler(event, context):
    
    function_beign = int (time.time()*1000)
    print("Global_aggregator_starting_Time = {}".format(function_beign))
    print(float(event[0]["delay"]))
    #print("Aggregator_invocation_delay {}".format(function_beign - float(event[0]["delay"])))
    print("Round time = {}".format(time.time() - event[0]["round_time"]))
    event[0]["epoch_time"] += time.time() - event[0]["round_time"]


    miniBatch_count = event[0]["miniBatch_count"] + 1
    epoch_count = event[0]["epoch_count"]
    total_epochs = event[0]["total_epochs"]
    total_workers = event[0]["total_clients"]
    num_shards = event[0]["num_shards"]
    total_mini_batches = event[0]["total_mini_batches"]
    round_time = event[0]["round_time"]
    shard_aggregator_id = event[0]["shard_aggregator_id"]
    num_shards = event[0]["num_shards"]
    batch_size = int(event[0]["batch_size"])
    event[0]["miniBatch_count"] += 1

    if event[0]["miniBatch_count"] > 0:
        time_download = int(time.time()*1000)
        dl_all(num_shards)
        print("aggregated_shard_download_time = {}".format(int(time.time()*1000) - time_download))
    
    my_data = launch_workers(event[0])
    print("Execution time {}".format(int(time.time()*1000) - function_beign ))
    return my_data

if __name__ == '__main__':
    event =[{'miniBatch_count': -1, 'round_time': 0, 'batch_size': 32, 'total_mini_batches': 157, 'epoch_count': 0, 'epoch_time': 0, 'total_clients': 10, 'delay': 1601528843055, 'shard_aggregator_id': 0, 'num_shards': 10, 'total_epochs': 4}]
    lambda_handler(event, "context")
