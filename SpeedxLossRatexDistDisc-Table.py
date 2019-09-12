#!/usr/bin/python3

## July/2019: This script pass through all speed and loss rate values to construct a data frame
# of speed, loss rate and discovery distances. It then saves the resulting data frame in a file named
# 'SpeedxLossRatexDistanceofDiscovery_***.csv'. The result is a table like the following one:

## These first data frames have the format: ###
# Unnamed      0  Speed   Loss Rate        D_n2        D_n3        D_n4
# 0            0  10kmh       lr0       198.595706  200.088847  199.907039
# 1            1  10kmh       lr15      200.765780  198.963031  200.472085
# 2            2  10kmh       lr30      190.385555  201.194559  195.601433
# 3            3  10kmh       lr45      185.371435  197.857639  199.385912
# 4            4  10kmh       lr60      199.159794  192.388433  198.339838
# 5            5  10kmh       lr75      196.389231  180.288338  197.192739

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
List_of_LossRates = ['lr0','lr15','lr30','lr45','lr60','lr75','lr90']

#############################################################################################
## General path for and solution
start_path ='/home/moraes/Doutorado/Traces/NewExperiments/and/'

################################################################################################
## Solutions' traces processing 															  ##
## The idea is to use traces of Periodic_Saved messages from node n1 in order to compute the  ##
## distance of discovery. This distance has to be computed from n1 to all other moving nodes. ##
## The main goal is to construct a 3D chart by cobining Speed, LossRate, Distance of Discovery##
################################################################################################
# A new df to keep data
col_names = ['Speed', 'Loss Rate', 'D_n2', 'D_n3', 'D_n4']
SpeedLRDistance_df = pd.DataFrame(columns = col_names)
# Using distance from n1 to all other moving nodes (n2 to n4) #
desired_idx = List_of_nodes.index("n1")

##### Running for all Speed values #####
for speed in List_of_speeds:
	## updating path
	path = start_path + speed
	for lr in List_of_LossRates:
		## final path to be used
		final_path = path + '/' + lr +'/'
	
		#### reading pre-processed traces of Periodic saved messages #####
		Sol01_Prdsvg_df_list = []
		## Periodic saved traces
		Sol01_prdsvg_msg_files = glob.glob(final_path + "*.Periodic.csv.done")
		## sorting in alphabetic order
		Sol01_prdsvg_msg_files.sort()
		
		# It's required to process one file per node
		for filename in Sol01_prdsvg_msg_files:
			## Reading traces
			Sol01_Prdsvg_df_list.append(pd.read_csv(filename))
		pass

		# a row structure to be added to the data frame
		row = {'Speed':speed, 'Loss Rate':lr, 'D_n2':0, 'D_n3':0, 'D_n4':0}
		## slicing dfs to get the distance of discovery (the first distance) ##
		for index,node in enumerate(List_of_nodes):
			if node != "n1": # Impossible to compute node's distance to itself
				if node in List_of_moving_nodes: ## using only moving nodes
					# taking the data frame related to 'n1'
					df_tmp = Sol01_Prdsvg_df_list[desired_idx]
					# select rows containing node
					df_tmp = df_tmp[df_tmp['List of Neighbors'].str.contains(node, na=False)]
					
					str_src = 'Distance_' + node
					str_dest = 'D_' + node
					if not df_tmp.empty:
						# It doesn't make sense to check the distance of discovery if the node was not discovered
						# select the first row (the first appearence of the node)
						row_tmp = df_tmp.iloc[0]
						# construct a new row to append to the resulting dataframe
						row[str_dest] = row_tmp[str_src]
					else:
						# If the node was not discoreved, set the distance to NaN
						row[str_dest] = float('NaN')
						print ("set to nan")
					pass	
				pass
			pass
		pass
		SpeedLRDistance_df = SpeedLRDistance_df.append(row, ignore_index=True)
	pass
pass

## save result to a file ##
# Result path
result_path ='/home/moraes/Doutorado/Traces/NewExperiments/and/'
suffix_name = "SpeedxLossRatexDistanceofDiscovery_and.csv"
file_name = result_path + suffix_name
SpeedLRDistance_df.to_csv(file_name)
