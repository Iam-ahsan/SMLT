import json
import boto3
import numpy as np
import PIL.Image as Image
import time
import tensorflow as tf
#import tensorflow_hub as hub
import updated_RL
IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224

#IMAGE_SHAPE = (IMAGE_WIDTH, IMAGE_HEIGHT)
#model = tf.keras.Sequential([hub.KerasLayer("model/")])
#model.build([None, IMAGE_WIDTH, IMAGE_HEIGHT, 3])

#imagenet_labels= np.array(open('model/ImageNetLabels.txt').read().splitlines())
s3 = boto3.resource('s3')

def lambda_handler(event, context): 
  function_beign = int (time.time()*1000)
  miniBatch_count = event["miniBatch_count"]
  epoch_count = event["epoch_count"] 
  total_workers = event["total_clients"]
  total_mini_batches = event["total_mini_batches"]
  worker_id = event["worker_id"]
  total_epochs = event["total_epochs"]
  round_time = event["round_time"]
  num_shards = int(event["num_shards"])
  batch_size = event["batch_size"]  
  print("Starting Training")
  
  updated_RL.my_train(num_shards, worker_id)

  
  response = {"epoch_count":epoch_count,"miniBatch_count":miniBatch_count, "total_clients":total_workers,
                "total_mini_batches":total_mini_batches,"total_epochs": total_epochs, "shard_aggregator_id":worker_id,
                "round_time":round_time, "num_shards": num_shards, "delay": int(time.time()*1000), 
                "epoch_time":event["epoch_time"], "batch_size":batch_size}
  print("Finish training")
  return response

  '''bucket_name = event['Records'][0]['s3']['bucket']['name']
  key = event['Records'][0]['s3']['object']['key']

  img = readImageFromBucket(key, bucket_name).resize(IMAGE_SHAPE)
  img = np.array(img)/255.0

  prediction = model.predict(img[np.newaxis, ...])
  predicted_class = imagenet_labels[np.argmax(prediction[0], axis=-1)]

  print('ImageName: {0}, Prediction: {1}'.format(key, predicted_class))'''

def readImageFromBucket(key, bucket_name):
  bucket = s3.Bucket(bucket_name)
  object = bucket.Object(key)
  response = object.get()
  return Image.open(response['Body'])

