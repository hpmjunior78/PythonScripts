#!/usr/bin/python3

## 12/06/2018: Plotting a 3D bar chart with Speed x Loss Rate x Distance of Discovery

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import


#############################################################################################
## Data path
data_path ='/home/moraes/Doutorado/Traces/AND/and/'
################################################################################################
### Final path for each solution ###
filename = "SpeedxLossRatexDistanceofDiscovery_and.csv"
final_path = data_path + filename

SpeedLRDistance_df = pd.read_csv(final_path)
#convert dataframe to matrix
SpeedLRDistance_values = SpeedLRDistance_df.values

#split matrix into 3 columns each into a 1d array
speed_values = SpeedLRDistance_df['Speed']
lossrate_values = SpeedLRDistance_df['Loss Rate']
discovery_distance = SpeedLRDistance_df['D_n2']

#converting into 1D array
speed_values = speed_values.ravel()
lossrate_values = lossrate_values.ravel()
discovery_distance = discovery_distance.ravel()

#### editing array's elements ####
## discovery distance
discovery_distance_array = []
for disc_dist in discovery_distance:
	## take values with precision of 2 terms (terms???)
	discovery_distance_array.append(disc_dist)
pass

## speed
final_speed_array = []
for speed_str in speed_values:
	## take the first two characters of the string
	speed = speed_str[:2]
	## convert string to integer
	final_speed_array.append(int(speed))
pass
## loss rate
final_lossrate_array = []
for lr_str in lossrate_values:
	## take characters from the third position to the end
	lr = lr_str[3:]
	## convert string to integer
	final_lossrate_array.append(int(lr))
pass

# print (final_lossrate_array)
# x = np.reshape(final_lossrate_array, (5,7))
# print (x)
# exit()

#### Plotting a surface chart ####
# setup the figure and axes
## A line chart ##
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

## Reshape arrays in 2 dimensional matrixes
x = np.reshape(final_speed_array, (5,7))
y = np.reshape(final_lossrate_array, (5,7))
z = np.reshape(discovery_distance_array, (5,7))
surface = ax.plot_surface(x,y,z, cmap=cm.winter)

## Chart title
title = fig.suptitle("AND algortihm - Statistics for node n1", fontsize=15)
ax.set_title("Variation of the Discovery Distance of node n2", fontsize=15)

## formating axis ##
# Speed = x axe
ax.set_xlabel('Speed (km/h)', color='g', fontsize=13)
ax.xaxis.set_ticks(np.arange(0, 100, 10))
ax.set_xlim(0, 100)

# Loss rate = y axe
ax.set_ylabel('Loss rate (%)', color='g', fontsize=13)
ax.yaxis.set_ticks(np.arange(0, 100, 15))
ax.set_ylim(0, 100)

# Distance of discovery = z axe
ax.set_zlabel('Discovery Distance', color='g', fontsize=12)
ax.zaxis.set_ticks(np.arange(0, 201, 20))
ax.set_zlim(0, 200)


plt.show()