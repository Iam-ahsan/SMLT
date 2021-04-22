import matplotlib.pyplot as plt
import numpy as np

def fit(x, y):
  a, b, c = np.polyfit(x, y, 2)
  x_n = np.array(list(range(-1, int(x[-1]), 10)))
  y_n = a * x_n * x_n + b * x_n + c
  return x_n, y_n

if __name__ == '__main__':
  ACC = [12.45, 48.35, 77.21, 80.12, 81.37, 82.95, 83.43, 84.03, 84.56, 84.92, 85.05, 85.01]
  ITERS = [0, 58, 116, 174, 232, 290, 348, 406, 464, 522, 580, 638]

  SMLT_Time = np.array(ITERS) * 4.7 # this is the per iter time
  CIRRUS_Time = np.array(ITERS) * 28.8 
  Siren_Time = np.array(ITERS) * 75.15

  fig = plt.figure()
  ax1 = fig.add_subplot(111)
  ax1.plot(SMLT_Time, ACC,  label='SMLT', color='black', marker='o', linestyle='dashed', linewidth=2, markersize=12)
  ax1.plot(CIRRUS_Time, ACC,  label='CIRRUS', color='black', marker='^', linestyle='dashed', linewidth=2, markersize=12)
  ax1.plot(Siren_Time, ACC, label='Siren', color='black', marker='*', linestyle='dashed', linewidth=2, markersize=12)
  plt.legend(loc='upper left');
  plt.show()

