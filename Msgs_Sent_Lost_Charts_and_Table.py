#!/usr/bin/python3

# July/2019: This script pass through all algorithms, speed and loss rate values to construct a data frame
# of messages sent and messages lost. It then saves the resulting data frame in a file named
# 'SpeedxLossRatexMsgSentLost_and.csv'. The result is a table like the following one:

#  ,Speed,Loss Rate,Msgs_sent,Msgs_lost
# 0,10kmh,     lr-0,      189,  17
# 1,10kmh,     lr-15,     192,  42
# 2,10kmh,     lr-30,     197,  75
# 3,10kmh,     lr-45,     219, 113


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
## Communication range in meters (a little bit larger than specified in AirPlug because it uses a random limitation of this range)
Comm_Range = 220
List_of_algorithms = ['and','etsi']
# Set the number of nodes here!! In alphabetical order!!
List_of_nodes = ['al1','al2','al3','al4','al5','al6','al7','al8', 'ap1','ap2','ap3','ap4','ap5','ap6','ap7','ap8','n1','n2','n3','n4']
List_of_moving_nodes = ['n1','n2','n3','n4']
## All speed values
List_of_speeds = ['10kmh','30kmh','50kmh','70kmh','90kmh']
# All loss-rate values
List_of_LossRates = ['lr-0','lr-15','lr-30','lr-45','lr-60','lr-75','lr-90']

# Using statistics from node n1
reference_node = 'n1'
reference_idx = List_of_nodes.index(reference_node)
# In relation to 'n2'
desired_node = 'n2'
desired_idx = List_of_nodes.index(desired_node)
#############################################################################################
## FUNCTIONS DEFINITIONS																   ##
#############################################################################################
#-- Function Normalize_values --------------------------------------------------------------#
# Action : Update all values in a column from a dataframe (numeric values only). The first	#
# 	one is taken as the starting time and all following values are updated accordingly. All	#
#	modifications are done in the received data frame. 										#
# Parameters : 								                                                #
#	- df:		data frame																	#
# 	- column 	column to be updated														#
# Return : none 																		    #
#-------------------------------------------------------------------------------------------#
def Normalize_values(df, column):
	ref_value = df.iloc[0][column]
	if pd.notnull(ref_value):
		df[column] = df[column].apply(lambda x: x - ref_value)
	return
#-- Function Compute_Lost_Messages ---------------------------------------------------------#
# Action : Compute the number of lost messages. Take every message sent (sentmsg_df) and	#
# search it on the received messages df (rcvdmsg_df). Check yet if the message received was #
# sent by the referenced node. 																#
# Parameters : 								                                                #
#	- sentmsg_df:	data frame of the sent messages 										#
#	- rcvdmsg_df:	data frame of received messages 										#
# Return : the number of lost messages													    #
#-------------------------------------------------------------------------------------------#
def Compute_Lost_Messages(sentmsg_df, rcvdmsg_df):

	# Reading sent-messages from data frame
	msgs_list = sentmsg_df['Seq. Number'].tolist()

	lost_messages = 0 # counter of lost messages
	messages_numb = 0
	# iterating through the list of seqeunce numbers
	for seq_number in msgs_list:
		messages_numb += 1
		## take rows where the sequence number was found
		rows = rcvdmsg_df.loc[rcvdmsg_df['Seq. Number'] == seq_number]
		# check wheter node (sender) is in the list of sending nodes...
		if reference_node not in rows['Sending Node(SN)'].values:
			# if it wasn't found, the message was lost
			lost_messages += 1
		pass
	pass
	#print ('==>', messages_numb, ' ==>', lost_messages)
	
	return lost_messages

################################################################################################
## Solutions' traces processing 															  ##
## The idea is to use traces of sent messages (*.Sent_Messages.csv) and of periodic saved     ##
## messages (*.Periodic.csv) from node n1 in order to compute the number of sent messages and ##
## the number of lost messages. The main goal is to construct a 3D-bar chart by cobining      ##
## Speed, LossRate and Number of messages 													  ##
################################################################################################
## General path
start_path ='/home/moraes/Doutorado/Traces/NewExperiments'

## Solution dictionary contains a list of data frames:
# - A list for all files related to the experiment executed with both solutions
Algos_df_dictionary = {}

## passing through all subfolders starting by the different algorithms
for alg in List_of_algorithms:
	## creating the data structure to hold all Solutions data
	try:
		## a silly statement to check data frame existence
		exist = Algos_df_dictionary[alg]
	except KeyError:
		Algos_df_dictionary[alg] = {} ## creating an empty dictionary
	pass
	alg_path = start_path + '/' + alg
	## then passing by all speed values
	for sp in List_of_speeds:
		try:
			exist = Algos_df_dictionary[alg][sp]
		except KeyError:
			Algos_df_dictionary[alg][sp] = {}
		pass
		speed_path = alg_path + '/' + sp
		## then passing by all loss rate values
		for lr in List_of_LossRates:
			try:
				exist = Algos_df_dictionary[alg][sp][lr]
			except KeyError:
				Algos_df_dictionary[alg][sp][lr] = []
			pass
			## Dictionary structure created. It's time to read data
			lossrate_path = speed_path + '/' + lr

			if os.path.exists(lossrate_path):
				print ("Processing files for %s" %alg, "at %s" %sp, "with %s as loss rate" %lr)
				## From already processed periodic-saved trace
				Prdsvg_msg_files = glob.glob(lossrate_path + '/' + "*.Periodic.csv.done")
				## sorting in alphabetic order
				Prdsvg_msg_files.sort()

				for filename in Prdsvg_msg_files:					
					try:
						## check if processed files exist
						Algos_df_dictionary[alg][sp][lr].append(pd.read_csv(filename))
					except:
						print ("===", filename, " not processed yet.. quitting ====="	)
						sys.exit()
					pass
				pass
			pass
		pass
	pass
pass

## Data structures with all algorithms, speed values and loss rate values ready for processing ##
# A new df to keep data
col_names = ['Speed', 'Loss Rate', 'Msgs_sent', 'Msgs_lost']
SpeedLRMessages_df = pd.DataFrame(columns = col_names)

##### Running for all Speed values #####
for speed in List_of_speeds:
	for lr in List_of_LossRates:
		## Keeping only required columns
		Sol01_Prdsvg_df = Sol01_Prdsvg_df_tmp[['TimeStamp','List of Neighbors','Distance_n2','Distance_n3','Distance_n4']].copy()
		
		## Keeping only values within the communication range (related to the desired node)
		dsrd_column = 'Distance_' + desired_node
		Sol01_Prdsvg_df = Sol01_Prdsvg_df.loc[Sol01_Prdsvg_df[dsrd_column] <= Comm_Range]

		## Getting values for slicing other dfs
		# get the first value of TimeStamp column in Sol01_Prdsvg_df slice
		first_TimeStamp = Sol01_Prdsvg_df.loc[Sol01_Prdsvg_df.index[0], 'TimeStamp']
		# get the last value of TimeStamp column in Sol01_Prdsvg_df slice
		last_TimeStamp = Sol01_Prdsvg_df.loc[Sol01_Prdsvg_df.index[-1], 'TimeStamp']
		
		#### reading pre-processed trace of sent messages #####
		# running for the desired node
		file_mask = '*' + reference_node + '*.Sent_Messages.csv'
		file = glob.glob(final_path + file_mask)
		Sol01_SentMsg_df = pd.read_csv(file[0])

		# a row structure to be added to the data frame
		row = {'Speed':speed, 'Loss Rate':lr, 'Msgs_sent':0, 'Msgs_lost':0}
		
		# Normalize TimeStamp values
		Normalize_values(Sol01_SentMsg_df, 'TimeStamp')
		
		# Slicing the dataframe in order to keep only values within the Comm. range
		Sol01_SentMsg_df = Sol01_SentMsg_df.loc[(Sol01_SentMsg_df['TimeStamp'] >= first_TimeStamp) & (Sol01_SentMsg_df['TimeStamp'] <= last_TimeStamp)]

		## To take the number of messages sent while a node is within other's communication range it's enough to take the first and the last
		# Sequence Numbers and subtract one from another.
		first_SeqNumber = Sol01_SentMsg_df.loc[Sol01_SentMsg_df.index[0], 'Seq. Number']
		last_SeqNumber = Sol01_SentMsg_df.loc[Sol01_SentMsg_df.index[-1], 'Seq. Number']
		
		## Saving the number of messages sent in the resulting data frame		
		row['Msgs_sent'] = last_SeqNumber - first_SeqNumber

		#### reading pre-processed trace of received messages #####
		## Compute the number of lost messages ##
		# I need the Received Messages Trace from the desired node
		file_mask = '*' + desired_node + '*.Received_Messages.csv'
		file = glob.glob(final_path + file_mask)
		Sol01_Rcvd_df_tmp = pd.read_csv(file[0])

		# Keeping only required columns
		Sol01_Rcvd_df = Sol01_Rcvd_df_tmp[['TimeStamp','Sending Node(SN)','Seq. Number','List of Neighbors']].copy()

		# Normalize TimeStamp values
		Normalize_values(Sol01_Rcvd_df, 'TimeStamp')

		# Slicing the dataframe in order to keep only values within the Comm. range
		Sol01_Rcvd_df = Sol01_Rcvd_df.loc[(Sol01_Rcvd_df['TimeStamp'] >= first_TimeStamp) & (Sol01_Rcvd_df['TimeStamp'] <= last_TimeStamp)]
		
		# save the number of lost messages
		row['Msgs_lost'] = Compute_Lost_Messages(Sol01_SentMsg_df, Sol01_Rcvd_df)

		## adding row to the final data frame
		SpeedLRMessages_df = SpeedLRMessages_df.append(row, ignore_index=True)
	pass
pass

## save result to a file ##
# Result path
result_path ='/home/moraes/Doutorado/Traces/AND/and/'
suffix_name = "SpeedxLossRatexMsgSentLost_and.csv"
file_name = result_path + suffix_name
SpeedLRMessages_df.to_csv(file_name)