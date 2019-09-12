#!/usr/bin/python3

## 12/06/2018: Plotting AND against ETSI
## There is a scenario with different configurations:
#			- Urban; Highway(Stopped node; Towards nodes; Traffic Jam)
# Plotting IMI, Lower Bound and Upper Bound

import matplotlib.pyplot as plt
from geopy.distance import vincenty ## Required to calculate distance between geographic points
import matplotlib.cm as cm
import pandas as pd
import numpy as np
import pylab as plb
import glob
import math
import copy
## modules for debugging.. erase them latter
import sys
import traceback
##set time range to perform slicing action
## value equals to 0.5 second in microseconds unit
time_range = 500000
# Set the number of nodes here!! In alphabetical order!!
List_of_nodes = ['al1','al2','al3','al4','al5','al6','al7','al8', 'ap1','ap2','ap3','ap4','ap5','ap6','ap7','ap8','n1','n2','n3','n4']
List_of_moving_nodes = ['n1','n2','n3','n4']
## All speed values
List_of_speeds = ['10kmh','30kmh','50kmh','70kmh','90kmh']
# All loss-rate values
List_of_LossRates = ['lr-0','lr-15','lr-30','lr-45','lr-60','lr-75','lr-90']
#############################################################################################
## FUNCTIONS DEFINITIONS																   ##
#############################################################################################
#-- Function Compute_Lost_Messages ---------------------------------------------------------#
# Action : Compute the number of lost messages per node. From every message sent, one by	#
# one, take its sequence number and search it in every received_messages data frame of 		#
# every other node.	If the was found, ok. If not, the message is considered lost.			#
# Parameters : 								                                                #
#	- node:			node whose messages are being computed									#
#	- msgs_list:	list of sent-messages taken from a data frame							#
# Return : none 																		    #
#-------------------------------------------------------------------------------------------#
def Compute_Lost_Messages(node, msgs_list):

	# Reading sent-messages from data frame
	#print ("==========", node, "=================")
	lost_messages = 0 # counter of lost messages
	messages_numb = 0
	# iterating through the list of seqeunce numbers
	for seq_number in msgs_list:
		lost_flag = 1 # flag equal to 1 means message lost.
		messages_numb += 1
		# search seq_number in other dfs
		#print ("====", seq_number, "====")
		for idx,nd in enumerate(List_of_nodes):
			# if it is not the node being verified
			if nd != node:
				#print ("==", nd, "==")
				## take rows where the sequence number was found
				rows = Sol01_Rcvd_df_list[idx].loc[Sol01_Rcvd_df_list[idx]['Seq. Number'] == seq_number]
				# check wheter node (sender) is in the list of sending nodes...
				if node in rows['Sending Node(SN)'].values:
					# if it was found, the message was received, i.e. not lost
					#print ('Found')
					lost_flag = 0
					#there is no need in keep searching
					break
				pass 
			pass
			#print ('.')
		pass
		# if the message was not found, increment the number of lost messages
		if lost_flag == 1:
			lost_messages += 1
		pass
	pass
	#print ('==>', messages_numb, ' ==>', lost_messages)
	
	return lost_messages

#############################################################################################
## General path for AND solution
start_path ='/home/moraes/Doutorado/Traces/AND/and/'

#############################################################################################

################################################################################################
## Solutions' traces processing 															  ##
## The idea is to use traces of sent messages (*.Sent_Messages.csv) and of periodic saved     ##
## messages (*.Periodic.csv) from node n1 in order to compute the number of sent messages and ##
## the number of lost messages. The main goal is to construct a 3D-bar chart by cobining      ##
## Speed, LossRate and Number of messages 													  ##
################################################################################################
######## Solution 01 ###########
# A new df to keep data
col_names = ['Speed', 'Loss Rate', 'Msgs_sent', 'Msgs_lost']
SpeedLRMessages_df = pd.DataFrame(columns = col_names)
# Using statistics from node n1
desired_node = 'n1'
desired_idx = List_of_nodes.index(desired_node)

##### Running for all Speed values #####
for speed in List_of_speeds:
	## updating path
	path = start_path + speed
	## running for all loss rate values
	for lr in List_of_LossRates:
		## final path to be used
		final_path = path + '/' + lr +'/'
	
		#### reading pre-processed trace of Periodic saved messages #####
		# running for the desired node
		file_mask = '*' + desired_node + '*.Periodic.csv'
		## Reading the periodic saved trace
		file = glob.glob(final_path + file_mask)
		Sol01_Prdsvg_df = pd.read_csv(file[0])

		#### reading pre-processed trace of sent messages #####
		# running for the desired node
		file_mask = '*' + desired_node + '*.Sent_Messages.csv'
		## Reading the periodic saved trace
		file = glob.glob(final_path + file_mask)
		Sol01_SentMsg_df = pd.read_csv(file[0])
		
		# a row structure to be added to the data frame
		row = {'Speed':speed, 'Loss Rate':lr, 'Msgs_sent':0, 'Msgs_lost':0}
		## It's not required to go through the DF. 
		
		## Taking the biggest Sequence Number of Sent Messages. 
		#It equals the number of sent messages!
		row['Msgs_sent'] = Sol01_SentMsg_df['Seq. Number'].max()
		## The number of lost messages is the sum of the column 
		# in Periodic saved trace
		row['Msgs_lost'] = Sol01_Prdsvg_df['Num. Lost Msgs'].sum()
		
		## adding row to the final data frame
		SpeedLRMessages_df = SpeedLRMessages_df.append(row, ignore_index=True)
		
	pass
pass

print (SpeedLRMessages_df)