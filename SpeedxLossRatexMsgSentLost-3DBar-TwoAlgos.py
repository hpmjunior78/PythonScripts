#!/usr/bin/python3

## 12/06/2018: Plotting a 3D bar chart with Speed x Loss Rate x Distance of Discovery

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import


#############################################################################################
## General data path
data_path ='/home/moraes/Doutorado/Traces/AND/'
################################################################################################
####### Final path for AND solution ########
filename = "and/SpeedxLossRatexMsgSentLost_and.csv"
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
Msgs_lost_values_and = Msgs_lost.ravel()

# Calculating a third messages array with the number of messages received
Msgs_rcvd_values_and = Msgs_sent_values - Msgs_lost_values_and

#### editing array's elements ####
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

####### Final path for ETSI solution ########
filename = "etsi/SpeedxLossRatexMsgSentLost_etsi.csv"
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
Msgs_lost_values_etsi = Msgs_lost.ravel()

# Calculating a third messages array with the number of messages received
Msgs_rcvd_values_etsi = Msgs_sent_values - Msgs_lost_values_etsi

#### editing array's elements ####
## speed
final_speed_array_etsi = []
for speed_str in speed_values:
	## take the first two characters of the string
	speed = speed_str[:2]
	## convert string to integer
	final_speed_array_etsi.append(int(speed))
pass
## loss rate
final_lossrate_array_etsi = []
for lr_str in lossrate_values:
	## take characters from the third position to the end
	lr = lr_str[3:]
	## convert string to integer
	final_lossrate_array_etsi.append(int(lr))
pass


########################################################
## Data ready, plotting the chart
########################################################
#### Plotting a 3D bar chart ####
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

### plotting AND values ###
# x(speed) and y(loss rate) values
xpos = [i -3 for i in final_speed_array_and]
ypos = final_lossrate_array_and
zpos = np.zeros(len(final_speed_array_and))

## Changing bars width
dx = [3] * len(final_speed_array_and)
dy = [3] * len(final_speed_array_and)

### z (messages) values ##
# I have two values for Z: Sent messages; Lost Messages
# I'm gonna plot in green the messages sent (not lost) and in red the messages lost
dz_rcvd = Msgs_rcvd_values_and
dz_lost = Msgs_lost_values_and

## plotting
ax.bar3d(xpos, ypos, zpos, dx, dy, dz_rcvd, color='g')
# add the height of each bar to know where to start the next
ax.bar3d(xpos, ypos, zpos+dz_rcvd, dx, dy, dz_lost, color='r')


### plotting ETSI values ###
# x(speed) and y(loss rate) values
xpos = [i +3 for i in final_speed_array_etsi]
ypos = final_lossrate_array_etsi
zpos = np.zeros(len(final_speed_array_etsi))

## Changing bars width
dx = [3] * len(final_speed_array_etsi)
dy = [3] * len(final_speed_array_etsi)

### z (messages) values ##
# I have two values for Z: Sent messages; Lost Messages
# I'm gonna plot in green the messages sent (not lost) and in red the messages lost
dz_rcvd = Msgs_rcvd_values_etsi
dz_lost = Msgs_lost_values_etsi

## plotting
ax.bar3d(xpos, ypos, zpos, dx, dy, dz_rcvd, color='b')
# add the height of each bar to know where to start the next
ax.bar3d(xpos, ypos, zpos+dz_rcvd, dx, dy, dz_lost, color=(1, 0.7, 0))
## Chart title
title = fig.suptitle("Messages sent by n1 and received or not by n2", fontsize=15)

## formating axis ##
# Speed = x axe
ax.set_xlabel('Speed (km/h)', color='g', fontsize=13)
ax.set_xticks([0, 10, 30, 50, 70, 90])
#ax.xaxis.set_ticks(np.arange(0, 100, 10))
#ax.set_xlim(0, 100)

# Loss rate = y axe
ax.set_ylabel('Loss rate (%)', color='g', fontsize=13)
ax.set_yticks([0, 15, 30, 45, 60, 75, 90])
#ax.yaxis.set_ticks(np.arange(0, 100, 15))
#ax.set_ylim(0, 100)

# Messages sent and lost = z axe
ax.set_zlabel('Messages', color='g', fontsize=12)
ax.zaxis.set_ticks(np.arange(0, 401, 25))
ax.set_zlim(0, 400)

#### Constructing the legend ######
lost_msg_and = plt.Rectangle((0, 0), 1, 1, fc="r")
rcvd_msg_and = plt.Rectangle((0, 0), 1, 1, fc="g")
legend_and = plt.legend([lost_msg_and, rcvd_msg_and],['Lost msgs','Received msgs'],title='AND', loc='upper left')
lost_msg_etsi = plt.Rectangle((0, 0), 1, 1, fc=(1, 0.7, 0))
rcvd_msg_etsi = plt.Rectangle((0, 0), 1, 1, fc="b")
legend_etsi = plt.legend([lost_msg_etsi, rcvd_msg_etsi],['Lost msgs','Received msgs'],title='ETSI', loc='upper right')
ax.add_artist(legend_and)
ax.add_artist(legend_etsi)

#ax.legend([lost_msg_and, lost_msg_etsi, rcvd_msg_and],['Lost msgs','Received msgs'])

plt.show()