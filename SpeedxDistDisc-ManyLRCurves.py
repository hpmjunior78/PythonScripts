#!/usr/bin/python3

## 12/06/2018: Plotting a 3D bar chart with Speed x Loss Rate x Distance of Discovery

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

# All loss-rate values
List_of_LossRates = ['lr-0','lr-15','lr-30','lr-45','lr-60','lr-75','lr-90']

#############################################################################################
## Data path
data_path ='/home/moraes/Doutorado/Traces/AND/'
################################################################################################
### Data frame for AND solution ###
filename = "and/SpeedxLossRatexDistanceofDiscovery_and.csv"
final_path = data_path + filename
AND_SpeedLRDistance_df = pd.read_csv(final_path)

### Data frame for ETSI solution ###
filename = "etsi/SpeedxLossRatexDistanceofDiscovery_etsi.csv"
final_path = data_path + filename
ETSI_SpeedLRDistance_df = pd.read_csv(final_path)

#### Plotting a 2D line chart ####
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111)

## Chart's main title
title = fig.suptitle("Distance of discovery - AND vs ETSI", fontsize=18)

## formating axis ##
# Speed = x axe
ax.set_xlabel('Speed', fontsize=14)
ax.set_xticks([0, 10, 30, 50, 70, 90])

# # Distance of discovery = y axe
ax.set_ylabel('Discovery Distance', fontsize=14)
ax.yaxis.set_ticks(np.arange(0, 221, 20))
ax.set_ylim(0, 220)

# plotted curves
and_curves = []
etsi_curves = []
## filtering and plotting by loss rate value
for LR in List_of_LossRates:
	AND_Partial_df = AND_SpeedLRDistance_df[AND_SpeedLRDistance_df['Loss Rate'] == LR]
	ETSI_Partial_df = ETSI_SpeedLRDistance_df[ETSI_SpeedLRDistance_df['Loss Rate'] == LR]

	## taking data separately
	#### selecting data for node n1 of Solution 02
	Speed_values = AND_Partial_df['Speed'].copy()
	## Cropping the speed string into integer values
	# Speed values are the same. There's no difference from AND to ETSI
	final_speed_values = []
	for speed_str in Speed_values:
		## take the first two characters of the string
		speed = speed_str[:2]
		## convert string to integer
		final_speed_values.append(int(speed))
	pass

	## Safety line (equals the distance travelled in 2 seconds)
	sl = ((2 * np.array(final_speed_values))/3.6) * 2

	## Distance of discovery values
	AND_Disc_Dist = AND_Partial_df['D_n2'].values
	ETSI_Disc_Dist = ETSI_Partial_df['D_n2'].values

	## Data ready, plotting the chart
	if LR == 'lr-60' or LR == 'lr-90':
		#'lr-0','lr-15','lr-30','lr-45','lr-60','lr-75','lr-90']
		# first, write the labels
		and_label = 'AND ' + LR
		etsi_label = 'ETSI ' + LR
		AND_Dist_line = ax.plot(final_speed_values, AND_Disc_Dist, lw=2, ls='-', label=and_label)
		ETSI_Dist_line = ax.plot(final_speed_values, ETSI_Disc_Dist, lw=2, ls='--', label=etsi_label)
	pass

pass

## Plotting the safety distance
ax.plot(final_speed_values,sl,c="red",linewidth=2,ls='-', label='Safety Distance')

#### legends ##
# first chart
lines = ax.get_lines()
ax.legend(lines, [line.get_label() for line in lines], loc='lower left', fontsize=16)

plt.show()