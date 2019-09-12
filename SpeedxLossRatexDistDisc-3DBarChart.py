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
data_path ='/home/moraes/Doutorado/Traces/AND/'
################################################################################################
### Final path for and solution ###
filename = "and/SpeedxLossRatexDistanceofDiscovery_and.csv"
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
discovery_distance_array_and = []
for disc_dist in discovery_distance:
	## take values with precision of 2 terms (terms???)
	discovery_distance_array_and.append(disc_dist)
pass

## speed
final_speed_array_and = []
for speed_str in speed_values:
	## take the first two characters of the string
	speed = speed_str[:2]
	## convert string to integer
	final_speed_array_and.append(int(speed))
pass
## loss rate
final_lossrate_array_and = []
for lr_str in lossrate_values:
	## take characters from the third position to the end
	lr = lr_str[3:]
	## convert string to integer
	final_lossrate_array_and.append(int(lr))
pass


### Final path for etsi solution ###
## Here, since the speed and loss rate values are the same, 
# only the Distance of discovery has to be read
filename = "etsi/SpeedxLossRatexDistanceofDiscovery_etsi.csv"
final_path = data_path + filename

SpeedLRDistance_df = pd.read_csv(final_path)
#convert dataframe to matrix
SpeedLRDistance_values = SpeedLRDistance_df.values

#split matrix into 3 columns each into a 1d array
discovery_distance = SpeedLRDistance_df['D_n2']

#converting into 1D array
discovery_distance = discovery_distance.ravel()

#### editing array's elements ####
## discovery distance
discovery_distance_array_etsi = []
for disc_dist in discovery_distance:
	## take values with precision of 2 terms (terms???)
	discovery_distance_array_etsi.append(disc_dist)
pass

########################################################
## Data ready, plotting the chart
########################################################
#### Plotting a 3D bar chart ####
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

### plotting ETSI values ###
# x(speed) and y(loss rate) values
xpos = final_speed_array_and
ypos = final_lossrate_array_and
zpos = np.zeros(len(final_speed_array_and))

## Changing bars width
dx = [3] * len(final_speed_array_and)
dy = [3] * len(final_speed_array_and)

### z (discovery distance) values ##
dz_etsi = discovery_distance_array_etsi
dz_and = discovery_distance_array_and

## printing bar per bar to avoid superpositioning. Idealy, starts from behind to front
# taking the list of loss rates in a reversed
for i,x in enumerate(xpos):
	# x represents the speed values
	# print etsi values in green
	ax.bar3d(x - 3, ypos[i], zpos[i], dx, dy, dz_etsi[i], color='g')
	# print and values in blue
	ax.bar3d(x + 3, ypos[i], zpos[i], dx, dy, dz_and[i], color='b')
	pass

## Chart's main title
title = fig.suptitle("Distance of discovery - AND vs ETSI", fontsize=15)
## formating axis ##
# Speed = x axe
ax.set_xlabel('Speed', color='g', fontsize=10)
#ax.xaxis.set_ticks()
ax.set_xticks([0, 10, 30, 50, 70, 90])
#ax.set_xlim(0, 100)

# Loss rate = y axe
ax.set_ylabel('Loss rate (%)', color='g', fontsize=10)
ax.set_yticks([0, 15, 30, 45, 60, 75, 90])
#ax.yaxis.set_ticks(np.arange(0, 100, 15))
#ax.set_ylim(0, 100)

# Distance of discovery = z axe
ax.set_zlabel('Discovery Distance', color='g', fontsize=9)
ax.zaxis.set_ticks(np.arange(0, 261, 20))
ax.set_zlim(0, 261)

# Inserting legend
etsi_leg = plt.Rectangle((0, 0), 1, 1, fc="g")
and_leg = plt.Rectangle((0, 0), 1, 1, fc="b")
ax.legend([etsi_leg, and_leg],['ETSI','AND'])


plt.show()