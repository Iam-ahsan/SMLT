import redis
import time
import pickle
import sys
import threading

r_connect = redis.Redis(host='3.236.19.198', port=6379)

def get_data(c_id, test, worker_id):
   vals = r_connect.get("lambda_data_{}".format(worker_id))
   #my_data = (np.array(pickle.loads(vals)))


def put_data(data, c_id, worker_id):
    r_connect.set("lambda_data_{}".format(worker_id),data)

def benchmarking(size, shards, worker_id):
    results = {}
    s = 'a'
    s1,e1,s2,e2 = 0, 0, 0, 0
    data = []
    threads = list()

    for i in range(size*1024):
        data.append(s)
    data = pickle.dumps(data)

    s1 =  (time.time()*1000000)
    for j in range(0,shards):
        put_data(data, j, worker_id)
        '''x = threading.Thread(target=put_data, args=(data, j))
        threads.append(x)
        x.start()
    for thread in threads:
        thread.join()'''

    e1 = (time.time()*1000000)

    s2 =  (time.time()*1000000)

    for j in range(0,shards):
        get_data(j, "test", worker_id)
        #y = threading.Thread(target=get_data, args=(j, "test"))  
        #threads.append(y)
        #y.start()
    #for thread in threads:
        #thread.join()

    e2 = (time.time()*1000000)
    results["put_time"] = (e1-s1)#/shards
    results["get_time"] = (e2-s2)#/shards
    print("put_time\t{}\tget_time\t{}".format(results["put_time"], results["get_time"]))
    return results
    
def lambda_handler(event, context):
    size = event["size"]
    shards = event["shards"]
    worker_id = event["worker"]
    results = benchmarking(int(size), int(shards),worker_id)
    #time.sleep(5)
    return results
    
if __name__ == "__main__":
    size = int(sys.argv[1])
    shards = int(sys.argv[2])
    benchmarking(size, shards)

