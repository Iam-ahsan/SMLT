import redis
import time
import pickle
import sys
import threading
import math
import numpy as np
import threading

#ip ="3.236.145.167"
#ports = ["7000", "7001", "7002", "7003", "7004", "7005"]
my_ips = ['3.235.242.221', '44.192.25.38', '3.235.175.83', '18.207.237.0', '3.238.98.88']
ports = ["7000"]*len(my_ips)
clinets = []
#for port in ports:
for i in range(len(ports)):
    clinets.append(redis.Redis(host=my_ips[i], port=ports[i]))
r_connect = redis.Redis(host=my_ips[0], port=ports[0])

def get_data(worker_id,shard_id):
   #r_connect = redis.Redis(host=ip, port=6379)
   #r_connect.get("sgd_worker_{}_shard_{}.pkl".format(worker_id,shard_id))
   clinets[worker_id%len(my_ips)].get("sgd-worker-{}-shard-{}".format(worker_id,shard_id))
   #vals = r_connect.get("sgd_worker_{}_shard_{}.pkl".format(worker_id,shard_id))
   return #vals


def put_data(data, worker_id, shard_id):
    r_connect.set("aggregated_shard_{}".format(shard_id),pickle.dumps(data))
    
def paralle_read(val, s_id):
    #print("I am here {}".format(s_id))
    data = pickle.loads(val)
    
def dl_sharded(shard_id, total_workers):
    i = 0
    threads = list()   
    while i < total_workers:
        #print("Download shard\t{}".format(i))
        s1 = (time.time()*1000)
        print("start_downloading_shard_id_{}_shard_{}\t{}".format(shard_id, i, s1))
        get_data(i, shard_id)
        e1 = (time.time()*1000)
        print("end_downloading_shard_id_{}_shard_{}\t{}".format(shard_id, i, e1))
        '''read_data = get_data(i, shard_id)    
        x = threading.Thread(target= paralle_read, args=(read_data,i))
        x.start()
        threads.append(x)'''
        i += 1
        
    #for thread in threads:
    #    thread.join()


def ul_agg_shard(shard_id,data):
    r_connect.set("aggregated_shard_{}".format(shard_id),pickle.dumps(data))




def dl_all(total_workers):
    i = 0
    threads = list()   
    while i < total_workers:
        read_data = r_connect.get("aggregated_shard_{}".format(i))
        i += 1
        x = threading.Thread(target= paralle_read, args=(read_data))
        threads.append(x)
        x.start()
    for thread in threads:
        thread.join()


def lambda_handler(event, context):
    
    function_beign = int (time.time()*1000)
    print("Shard_aggregator_starting_Time = {}".format(function_beign))
    print("Manager_invocation_delay {}".format(function_beign - event["delay"]))
    print('Got asked to aggregate...')


    #total_shards = event["total_shards"]
    miniBatch_count = event["miniBatch_count"]
    epoch_count = event["epoch_count"] 
    total_clients = event["total_clients"]
    total_mini_batches = event["total_mini_batches"]
    aggregator_id = event["aggregator_id"]
    total_epochs = event["total_epochs"]
    round_time = event["round_time"]
    total_shards = event["num_shards"]
   
    s1 = (time.time()*1000)
    print("start_overall_download_shard_id_{}\t{}".format(aggregator_id, s1))
    dl_sharded(aggregator_id, total_shards) 
    e1 = (time.time()*1000)
    print("finish_overall_download_shard_id_{}\t{}".format(aggregator_id, e1))
    print("shard_download_time\t{}".format(e1 - s1))

    data = pickle.loads(clinets[0].get("sgd-worker-{}-shard-{}".format(0,aggregator_id%total_shards)))
    s2 = (time.time()*1000)
    ul_agg_shard(aggregator_id,data)
    e2 = (time.time()*1000)
    print("aggregated_shard_upload_time\t{}".format(e2-s2))
    response = {"miniBatch_count":miniBatch_count, "total_clients":total_clients, 
                "epoch_count":epoch_count,"total_mini_batches":total_mini_batches,
            "total_epochs": total_epochs, "shard_aggregator_id":aggregator_id, "round_time":round_time,
             "num_shards": total_shards, "delay": int(time.time()*1000), "epoch_time":event["epoch_time"], "batch_size": event["batch_size"]}
 
    print("Shard_aggregator_execution_time\t{}".format(e2-s1))
    return response
if __name__ == '__main__':
    event = {
    "delay":0,
 "total_shards":10,
  "miniBatch_count": 0,
  "epoch_count": 0,
  "total_clients": 5,
  "total_mini_batches": 1,
  "aggregator_id": 0,
  "total_epochs": 30,
  "round_time": 0,
  "num_shards": 10,
  "epoch_time":0,
  "batch_size":32
}
    print("I am here")
    lambda_handler(event, "context")
