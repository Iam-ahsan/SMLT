"""
Title: Deep Q-Learning for Atari Breakout
Author: [Jacob Chapman](https://twitter.com/jacoblchapman) and [Mathias Lechner](https://twitter.com/MLech20)
Date created: 2020/05/23
Last modified: 2020/06/17
Description: Play Atari Breakout with a Deep Q-Network.
"""
"""
## Introduction

This script shows an implementation of Deep Q-Learning on the
`BreakoutNoFrameskip-v4` environment.

### Deep Q-Learning

As an agent takes actions and moves through an environment, it learns to map
the observed state of the environment to an action. An agent will choose an action
in a given state based on a "Q-value", which is a weighted reward based on the
expected highest long-term reward. A Q-Learning Agent learns to perform its
task such that the recommended action maximizes the potential future rewards.
This method is considered an "Off-Policy" method,
meaning its Q values are updated assuming that the best action was chosen, even
if the best action was not chosen.

### Atari Breakout

In this environment, a board moves along the bottom of the screen returning a ball that
will destroy blocks at the top of the screen.
The aim of the game is to remove all blocks and breakout of the
level. The agent must learn to control the board by moving left and right, returning the
ball and removing all the blocks without the ball passing the board.

### Note

The Deepmind paper trained for "a total of 50 million frames (that is, around 38 days of
game experience in total)". However this script will give good results at around 10
million frames which are processed in less than 24 hours on a modern machine.

### References

- [Q-Learning](https://link.springer.com/content/pdf/10.1007/BF00992698.pdf)
- [Deep Q-Learning](https://deepmind.com/research/publications/human-level-control-through-deep-reinforcement-learning)
"""
"""
## Setup
"""

from atari_wrappers import make_atari, wrap_deepmind
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import time
import pickle
import sys
import redis
import math

''''seed = 42
gamma = 0.99 
epsilon = 1.0 
epsilon_min = 0.1 
epsilon_max = 1.0
epsilon_interval = (
    epsilon_max - epsilon_min
) 
batch_size = 32 
max_steps_per_episode = 10000
env = make_atari("BreakoutNoFrameskip-v4")
env = wrap_deepmind(env, frame_stack=True, scale=True)
env.seed(seed)'''

"""
## Implement the Deep Q-Network

This network learns an approximation of the Q-table, which is a mapping between
the states and actions that an agent will take. For every state we'll have four
actions, that can be taken. The environment provides the state, and the action
is chosen by selecting the larger of the four Q-values predicted in the output layer.

"""
my_ips = ['3.235.242.221']#, '44.192.25.38', '3.235.175.83']#['3.235.242.221']
ports = ["7000"]*len(my_ips)
num_actions = 4
clinets = []
for i in range(len(ports)):
    clinets.append(redis.Redis(host=my_ips[i], port=ports[i]))
#redis_client = redis.Redis(host=my_ips[worker_id%len(my_ips)], port=ports[worker_id%len(my_ips)])

def create_q_model():
    # Network defined by the Deepmind paper
    inputs = layers.Input(shape=(84, 84, 4,))
    layer1 = layers.Conv2D(32, 8, strides=4, activation="relu")(inputs)
    layer2 = layers.Conv2D(64, 4, strides=2, activation="relu")(layer1)
    layer3 = layers.Conv2D(64, 3, strides=1, activation="relu")(layer2)
    layer4 = layers.Flatten()(layer3)
    layer5 = layers.Dense(512, activation="relu")(layer4)
    #layer6 = layers.Dense(1024, activation="relu")(layer5)
    #layer7 = layers.Dense(2048, activation="relu")(layer6)
    action = layers.Dense(num_actions, activation="linear")(layer5)
    return keras.Model(inputs=inputs, outputs=action)

model = create_q_model()
model_target = create_q_model()

def shard_data(shards, worker_id):
    data = []
    with open ("my_data.pkl", 'rb') as fp:
        data = pickle.load(fp)
    redis_client = clinets[worker_id%len(my_ips)]#redis.Redis(host=my_ips[worker_id%len(my_ips)], port=ports[worker_id%len(my_ips)])
    increment = int(math.ceil(len(data) /float(shards)))
    final_val = 0
    f_time = int(time.time()*1000)
    for i in range(shards):
        file_name = "sgd-worker-{}-shard-{}".format(worker_id,i)
        final_val =  min(len(data), (i*increment)+increment)
        starting = i*increment
        redis_client.set(file_name, pickle.dumps(data[starting:final_val]))  
        #print(final_val,'\t', starting, '\t', final_val-starting)
        #with open('./sgd/shard_{}'.format(i),'wb') as fp:
        #    pickle.dump(data[starting:final_val], fp)
    fe_time = int(time.time()*1000)
    print("upload_sharded_sgd_time\t{}".format(fe_time - f_time))
    #time.sleep(3)
    s1 = (time.time()*1000)
    dl_sharded(worker_id, shards)
    e1 = (time.time()*1000)
    print("shard_download_time\t{}".format(e1 - s1))
    s2 = (time.time()*1000)
    ul_agg_shard(worker_id,data[starting:final_val])
    e2 = (time.time()*1000)
    print("aggregated_shard_upload_time\t{}".format(e2-s2))
    

def get_data(worker_id,shard_id):
   clinets[worker_id%len(my_ips)].get("sgd-worker-{}-shard-{}".format(worker_id,shard_id))
   return 

def ul_agg_shard(shard_id,data):
    clinets[shard_id%len(my_ips)].set("aggregated_shard_{}".format(shard_id),pickle.dumps(data))

def dl_sharded(shard_id, total_workers):
    i = 0
    while i < total_workers:
        #print("Download shard\t{}".format(i))
        #s1 = (time.time()*1000)
        #print("start_downloading_shard_id_{}_shard_{}\t{}".format(shard_id, i, s1))
        get_data(i, shard_id)
        i += 1
        #e1 = (time.time()*1000)
        #print("end_downloading_shard_id_{}_shard_{}\t{}".format(shard_id, i, e1))

    
"""
## Train
"""
def my_train(shards, worker_id):
    seed = 42
    gamma = 0.99
    epsilon = 1.0
    epsilon_min = 0.1
    epsilon_max = 1.0
    epsilon_interval = (
    epsilon_max - epsilon_min)
    batch_size = 32
    max_steps_per_episode = 10000
    env = make_atari("BreakoutNoFrameskip-v4")
    env = wrap_deepmind(env, frame_stack=True, scale=True)
    env.seed(seed)
    num_actions = 4

    optimizer = keras.optimizers.Adam(learning_rate=0.00025, clipnorm=1.0)
    action_history = []
    state_history = []
    state_next_history = []
    rewards_history = []
    done_history = []
    episode_reward_history = []
    running_reward = 0
    episode_count = 0
    frame_count = 0

    epsilon_random_frames = 50000
    epsilon_greedy_frames = 1000000.0

    # Note: The Deepmind paper suggests 1000000 however this causes memory issues
    max_memory_length = 100000

    # Train the model after 4 actions
    update_after_actions = 50000//shards
    # How often to update the target network
    update_target_network = 10000
    loss_function = keras.losses.Huber()
    s_time =  time.time()*1000
    while True:  # Run until solved
        state = np.array(env.reset())
        episode_reward = 0
        for timestep in range(1, max_steps_per_episode):
            frame_count += 1
            if frame_count < epsilon_random_frames or epsilon > np.random.rand(1)[0]:
                # Take random action
                action = np.random.choice(num_actions)
            else:
                # Predict action Q-values
                # From environment state
                state_tensor = tf.convert_to_tensor(state)
                state_tensor = tf.expand_dims(state_tensor, 0)
                action_probs = model(state_tensor, training=False)
                # Take best action
                action = tf.argmax(action_probs[0]).numpy()

            # Decay probability of taking random action
            epsilon -= epsilon_interval / epsilon_greedy_frames
            epsilon = max(epsilon, epsilon_min)

            # Apply the sampled action in our environment
            # the env.step() function should be a communication function
            #   the env.step takes place in a different serverless function
            #   and returns the state_next, reward and done values
            # ----------------

            state_next, reward, done, _ = env.step(action)
            state_next = np.array(state_next)

            episode_reward += reward

            # Save actions and states in replay buffer
            action_history.append(action)
            state_history.append(state)
            state_next_history.append(state_next)
            done_history.append(done)
            rewards_history.append(reward)
            state = state_next
            
            # Once you have enough env.step() function returns
            #   meaning enough actions are complete
            # do a forward pass
            # So it is basically like a batch size, number of actions is equivalent
            # to batch size
            # ----- FORWARD PASS START----------------
            #print(batch_size)
            if frame_count % update_after_actions == 0 and len(done_history) > batch_size:
                data = {}
                data['action_history'] = action_history
                data['state_history'] = state_history
                data['state_next_history'] = [state_next_history]
                data['done_history'] = done_history
                data['reward_history'] = rewards_history
                data['state'] = state
                #with open ('input_data.pkl', 'wb') as fp:
                #    pickle.dump(data, fp)
                #sys.exit()
                # Get indices of samples for replay buffers
                sm_time =  time.time()*1000
                print("Simulation_time\t{}".format(sm_time-s_time))
                indices = np.random.choice(range(len(done_history)), size=batch_size)

                # Using list comprehension to sample from replay buffer
                state_sample = np.array([state_history[i] for i in indices])
                state_next_sample = np.array([state_next_history[i] for i in indices])
                rewards_sample = [rewards_history[i] for i in indices]
                action_sample = [action_history[i] for i in indices]
                done_sample = tf.convert_to_tensor(
                    [float(done_history[i]) for i in indices]
                )

                # Build the updated Q-values for the sampled future states
                # Use the target model for stability
                future_rewards = model_target.predict(state_next_sample)
                # Q value = reward + discount factor * expected future reward
                updated_q_values = rewards_sample + gamma * tf.reduce_max(
                    future_rewards, axis=1
                )

                # If final frame set the last value to -1
                updated_q_values = updated_q_values * (1 - done_sample) - done_sample

                # Create a mask so we only calculate loss on the updated Q-values
                masks = tf.one_hot(action_sample, num_actions)

                with tf.GradientTape() as tape:
                    # Train the model on the states and updated Q-values
                    q_values = model(state_sample)

                    # Apply the masks to the Q-values to get the Q-value for action taken
                    q_action = tf.reduce_sum(tf.multiply(q_values, masks), axis=1)
                    # Calculate loss between new Q-value and old Q-value
                    loss = loss_function(updated_q_values, q_action)

                grads = tape.gradient(loss, model.trainable_variables)
                # ------- FORWARD PASS FINISHED ----------
                # Now we have the gradients for the batch

                # Uncomment for generating gradients file
                
                
                #with open('/tmp/atari_rl_grads.pkl', 'wb') as fp:
                #    pickle.dump(grads, fp)
                #print("Extracted gradients")
                e_time = time.time()*1000
                print("Pure_training_time\t{}".format(e_time-sm_time))
                shard_data(shards, worker_id)
                print("Total time {}".format(e_time-s_time))
                return
                #import sys
                #sys.exit()
                
                #with open('atari_rl_grads.pkl', 'rb') as fp:
                #    grads = pickle.load(fp)'''
                

                # ---- BACK-PROP --------#
                optimizer.apply_gradients(zip(grads, model.trainable_variables))

            if frame_count % update_target_network == 0:
                # update the the target network with new weights
                model_target.set_weights(model.get_weights())
                # Log details
                template = "running reward: {:.2f} at episode {}, frame count {}"
                print(template.format(running_reward, episode_count, frame_count))

            # Limit the state and reward history
            if len(rewards_history) > max_memory_length:
                del rewards_history[:1]
                del state_history[:1]
                del state_next_history[:1]
                del action_history[:1]
                del done_history[:1]

            if done:
                break

        # Update running reward to check condition for solving
        episode_reward_history.append(episode_reward)
        if len(episode_reward_history) > 100:
            del episode_reward_history[:1]
        running_reward = np.mean(episode_reward_history)

        episode_count += 1

        if running_reward > 40:  # Condition to consider the task solved
            print("Solved at episode {}!".format(episode_count))
            break

def lambda_handler(event, context):
    shards = event['shards']
    worker_id = event['worker_id']
    my_train(shards, worker_id)

if __name__ == '__main__':
    my_train()
