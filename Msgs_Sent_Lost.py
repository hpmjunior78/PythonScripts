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
# Return : none 																			#
# Note: Pay attention to nodes alone. Their sent messages won't be received by any other	#
# 	node. How to control this???														    #
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
			if nd == 'n2':
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
## The idea is to use traces of sent messages (*.Sent_Messages.csv) and of received messages  ##
## (*.Received_Messages.csv) from node n1 in order to compute the number of sent messages and ##
## the number of lost messages. The main goal is to construct a 3D-bar chart by cobining      ##
## Speed, LossRate and Number of messages 													  ##
################################################################################################
######## Solution 01 ###########
print ("==========================================")
print ("Solutions_01 traces processing - AND, 10km/h, lr-90")
Sol01_path = start_path + '10kmh/lr-90/'
## From sent-messages-trace take IMI
Sol01_sent_msg_files = glob.glob(Sol01_path + "*.Sent_Messages.csv")
## Received-messages-traces required to compute the number of messages lost
Sol01_rcvd_msg_files = glob.glob(Sol01_path + "*.Received_Messages.csv")
## sorting in alphabetic order
Sol01_sent_msg_files.sort()
Sol01_rcvd_msg_files.sort()

### Reading traces of sent messages ###
Sol01_Sent_df_list_tmp = []
for filename in Sol01_sent_msg_files:
    Sol01_Sent_df_list_tmp.append(pd.read_csv(filename))
    pass

## Cropping out columns and lines without use from Sent Messages data frames
Sol01_Sent_df_list = []
Sol01_Number_Sent_Msg_list = []
for df in Sol01_Sent_df_list_tmp:
	## Taking the biggest Sequence Number of Sent Messages. It equals the number of sent messages!
	Sol01_Number_Sent_Msg_list.append(df['Seq. Number'].max())
	## taking off IMI values out of the range. Usually the first IMI value is not correct
	df = df[df.IMI < 10000]
	## crop out other values
	Sol01_Sent_df_list.append(df[['TimeStamp', 'Seq. Number', 'IMI']].copy())
pass

### Reading traces of received messages ###
Sol01_Rcvd_df_list_tmp = []
for filename in Sol01_rcvd_msg_files:
    Sol01_Rcvd_df_list_tmp.append(pd.read_csv(filename))
    pass

## Cropping out columns and lines without use from Received Messages data frames
Sol01_Rcvd_df_list = []
for df in Sol01_Rcvd_df_list_tmp:
	## crop out other values
	Sol01_Rcvd_df_list.append(df[['TimeStamp','Sending Node(SN)','Seq. Number','List of Neighbors']].copy())
pass

## ------------------------------------- ##
## Computing the number of lost messages
Sol01_Number_Lost_Msg_list = []
for index,node in enumerate(List_of_nodes):
	# for every node, take its list of messages sent (sequence number only)
	Sent_Msgs_List = Sol01_Sent_df_list[index]["Seq. Number"].tolist()
	## call function to check how many messages were lost
	if node == 'n1':
		Sol01_Number_Lost_Msg_list.append(Compute_Lost_Messages(node, Sent_Msgs_List))
	pass
pass

print ('***** Resultado ********')
#for index,node in enumerate(List_of_nodes):
#	print (node, Sol01_Number_Sent_Msg_list[index],' | ', Sol01_Number_Lost_Msg_list[index])
#pass
print (Sol01_Number_Sent_Msg_list,' | ', Sol01_Number_Lost_Msg_list)