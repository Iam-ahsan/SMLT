from bayes_opt import BayesianOptimization
from bayes_opt import UtilityFunction
import numpy as np
import json

import matplotlib .pyplot as plt 
from matplotlib import gridspec

def target(x):
    print("I am here {}".format(x))
    return np.exp(-(x-2)**2)+ np.exp(-(x-6)**2/10) + 1/(x**2+1)

def my_target(x):
    data = {}
    with open("my_training", 'r') as fp:
        data= json.load(fp)
    y = data['data']
    print(len(y))
    print(x)
    return y[int(x)-10] 

def posterior(optimizer, x_obs, y_obs, grid):
    optimizer._gp.fit(x_obs, y_obs)

    mu, sigma = optimizer._gp.predict(grid, return_std=True)
    return mu, sigma


def plot_gp(optimizer, x, y):
    fig = plt.figure(figsize=(16, 10))
    steps = len(optimizer.space)
    fig.suptitle(
        'Gaussian Process and Utility Function After {} Steps'.format(steps),
        fontdict={'size':30}
    )

    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    axis = plt.subplot(gs[0])
    

    x_obs = np.array([[res["params"]["x"]] for res in optimizer.res])
    y_obs = np.array([res["target"] for res in optimizer.res])
    
    mu, sigma = posterior(optimizer, x_obs, y_obs, x)
    axis.plot(x, y, linewidth=3, label='Target')
    axis.plot(x_obs.flatten(), y_obs, 'D', markersize=8, label=u'Observations', color='r')
    axis.plot(x, mu, '--', color='k', label='Prediction')
    
    axis.fill(np.concatenate([x, x[::-1]]),
              np.concatenate([mu - 1.9600 * sigma, (mu + 1.9600 * sigma)[::-1]]),
        alpha=.6, fc='c', ec='None', label='95% confidence interval')
    axis.plot(optimizer.max['params']['x'], max(mu), '*', markersize=15,
             label=u'Optimal workers', markerfacecolor='gold', markeredgecolor='k', markeredgewidth=1) 
    axis.set_xlim((5, 100))
    axis.set_ylim((None, None))
    axis.set_ylabel('f(x)', fontdict={'size':20})
    axis.set_xlabel('x', fontdict={'size':20})
    plt.savefig('BO.pdf')
    
    utility_function = UtilityFunction(kind="ucb", kappa=5, xi=0)
    utility = utility_function.utility(x, optimizer._gp, 0)
    
    axis.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)
    plt.show()


def run_optimization(my_last):
    #x = np.linspace(-2,10,1000).reshape(-1,1)
    #y = target(x) #.reshape(-1,1)
    data = {}
    with open("my_training", 'r') as fp:
        data= json.load(fp)
    y = data['data']
    x = np.linspace(10,10+len(y),len(y)).reshape(-1,1)
    
    
    optimizer = BayesianOptimization(my_target, {'x':(10, my_last-1)}, random_state=27)
    optimizer.maximize(init_points=2, n_iter=3, kappa=5)
    plot_gp(optimizer, x, y)
 
if __name__ == '__main__':
    
    data = {}
    with open("my_training", 'r') as fp:
        data= json.load(fp)
    y = data['data']
    
    x = np.linspace(10,10+len(y),len(y)).reshape(-1,1)
     
    optimizer = BayesianOptimization(my_target, {'x':(10,100)}, random_state=27)
    optimizer.maximize(init_points=2, n_iter=3, kappa=5)
    plot_gp(optimizer, x, y)
    print(optimizer.max)
    
