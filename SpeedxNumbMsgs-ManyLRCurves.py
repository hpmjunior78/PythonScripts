#!/usr/bin/python3

## 12/06/2018: Plotting a 2D line chart with Speed x Number of messages
## Two curves (Received, Lost messages) are plotted for each solution (AND, ETSI)  at every LR value.

import pandas as pd
import numpy as np
import pylab as plb
import matplotlib.pyplot as plt
from matplotlib import cm


# All loss-rate values
List_of_LossRates = ['lr0','lr15','lr30','lr45','lr60','lr75','lr90']

#############################################################################################
## Data path
data_path ='/home/moraes/Doutorado/Traces/NewExperiments/'
################################################################################################
### Data frame for AND solution ###
filename = "and/SpeedxLossRatexMsgSentLost_and.csv"
final_path = data_path + filename
AND_SpeedLRMsgSentLost_df = pd.read_csv(final_path)

### Data frame for ETSI solution ###
filename = "etsi/SpeedxLossRatexMsgSentLost_etsi.csv"
final_path = data_path + filename
ETSI_SpeedLRMsgSentLost_df = pd.read_csv(final_path)

#### Plotting a 2D line chart ####
fig = plt.figure(figsize=(13, 7))
ax = fig.add_subplot(111)

## Chart's main title
title = fig.suptitle("AND vs ETSI - Number of messages sent", fontsize=18)
## subtitle
#plt.title("AND vs ETSI with a loss rate of 90%", fontsize=16)
## formating axis ##
# Speed = x axe
ax.set_xlabel('Speed', fontsize=14)
ax.set_xticks([0, 10, 30, 50, 70, 90])

# # Distance of discovery = y axe
ax.set_ylabel('Number of messages', fontsize=14)
ax.yaxis.set_ticks(np.arange(0, 249, 20))
ax.set_ylim(0, 250)

# plotted curves
and_curves = []
etsi_curves = []
## filtering and plotting by loss rate value
for LR in List_of_LossRates:
	AND_Partial_df = AND_SpeedLRMsgSentLost_df[AND_SpeedLRMsgSentLost_df['Loss Rate'] == LR]
	ETSI_Partial_df = ETSI_SpeedLRMsgSentLost_df[ETSI_SpeedLRMsgSentLost_df['Loss Rate'] == LR]

	## taking data separately
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

	## Number of messages sent
	AND_Sent_Msgs = AND_Partial_df['Msgs_sent'].values
	ETSI_Sent_Msgs = ETSI_Partial_df['Msgs_sent'].values

	## Number of messages lost
	AND_Lost_Msgs = AND_Partial_df['Msgs_lost'].values
	ETSI_Lost_Msgs = ETSI_Partial_df['Msgs_lost'].values

	## Data ready, plotting the chart
	if LR == 'lr60' or LR == 'lr90':
		#'lr-0','lr-15','lr-30','lr-45','lr-60','lr-75','lr-90']
		# first, write the labels
		# and_label_sent = 'AND ' + '- Sent msgs'# + LR 
		# etsi_label_sent = 'ETSI ' + '- Sent msgs'# + LR 
		
		# and_label_lost = 'AND ' + '- Lost msgs'# + LR
		# etsi_label_lost = 'ETSI ' + '- Lost msgs'# + LR

		# first, write the labels
		and_label = 'AND ' + LR 
		etsi_label = 'ETSI ' + LR 

		AND_SentMsgs_line = ax.plot(final_speed_values, AND_Sent_Msgs, lw=2, ls='-', label=and_label)
		#AND_LostMsgs_line = ax.plot(final_speed_values, AND_Lost_Msgs, lw=2, ls='--', label=and_label_lost)

		ETSI_SentMsgs_line = ax.plot(final_speed_values, ETSI_Sent_Msgs, lw=2, ls='--', label=etsi_label)
		#ETSI_LostMsgs_line = ax.plot(final_speed_values, ETSI_Lost_Msgs, lw=2, ls='--', label=etsi_label_lost)
	pass
	

pass

#### legends ##
# first chart
lines = ax.get_lines()
ax.legend(lines, [line.get_label() for line in lines], loc='upper right', fontsize=16)

# Charts path
charts_path ='/home/moraes/Doutorado/Charts/NewExperiments-02/2D-Charts/'
suffix_name = "SpeedxMsgSentLost-ANDvsETSI-lr60-90-2019-5-30.png"
file_name = charts_path + suffix_name
plb.savefig(file_name)