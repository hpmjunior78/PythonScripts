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
data_path ='/home/moraes/Doutorado/Traces/AND/etsi/'
################################################################################################
### Final path for each solution ###
filename = "SpeedxLossRatexMsgSentLost_etsi.csv"
final_path = data_path + filename

SpeedLRMsgSentLost_df = pd.read_csv(final_path)
#convert dataframe to matrix
SpeedLRMsgSentLost_values = SpeedLRMsgSentLost_df.values

#split matrix into 3 columns each into a 1d array
speed_values = SpeedLRMsgSentLost_df['Speed']
lossrate_values = SpeedLRMsgSentLost_df['Loss Rate']
Msgs_sent = SpeedLRMsgSentLost_df['Msgs_sent']
Msgs_lost = SpeedLRMsgSentLost_df['Msgs_lost']

#converting into 1D array
speed_values = speed_values.ravel()
lossrate_values = lossrate_values.ravel()
Msgs_sent_values = Msgs_sent.ravel()
Msgs_lost_values = Msgs_lost.ravel()

# Calculating a third messages array with the number of messages received
Msgs_rcvd_values = Msgs_sent_values - Msgs_lost_values

#### editing array's elements ####
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

#### Plotting a 3D bar chart ####
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

# x(speed) and y(loss rate) values
xpos = final_speed_array
ypos = final_lossrate_array
zpos = np.zeros(len(final_speed_array))

## Changing bars width
dx = [3] * len(final_speed_array)
dy = [3] * len(final_speed_array)

### z (messages) values ##
# I have two values for Z: Sent messages; Lost Messages
# I'm gonna plot in green the messages sent (not lost) and in red the messages lost
dz_rcvd = Msgs_rcvd_values
dz_lost = Msgs_lost_values

## plotting
ax.bar3d(xpos, ypos, zpos, dx, dy, dz_rcvd, color='g')
# add the height of each bar to know where to start the next
ax.bar3d(xpos, ypos, zpos+dz_rcvd, dx, dy, dz_lost, color='r')

## Chart title
title = fig.suptitle("ETSI algortihm - Messages sent by n1 and received or not by n2", fontsize=15)

## formating axis ##
# Speed = x axe
ax.set_xlabel('Speed (km/h)', color='g', fontsize=13)
ax.xaxis.set_ticks(np.arange(0, 100, 10))
ax.set_xlim(0, 100)

# Loss rate = y axe
ax.set_ylabel('Loss rate (%)', color='g', fontsize=13)
ax.yaxis.set_ticks(np.arange(0, 100, 15))
ax.set_ylim(0, 100)

# Messages sent and lost = z axe
ax.set_zlabel('Messages', color='g', fontsize=12)
ax.zaxis.set_ticks(np.arange(0, 401, 25))
ax.set_zlim(0, 400)

# Inserting legend
lost_msg = plt.Rectangle((0, 0), 1, 1, fc="r")
rcvd_msg = plt.Rectangle((0, 0), 1, 1, fc="g")
ax.legend([lost_msg,rcvd_msg],['Lost msgs','Received msgs'])

plt.show()