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
## General path for AND solution
start_path ='/home/moraes/Doutorado/Traces/AND/etsi/'

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
					# select the first row (the first appearence of the node)
					row_tmp = df_tmp.iloc[0]
					# construct a new row to append to the resulting dataframe
					str_src = 'Distance_' + node
					str_dest = 'D_' + node
					row[str_dest] = row_tmp[str_src]
				pass
			pass
		pass
		SpeedLRDistance_df = SpeedLRDistance_df.append(row, ignore_index=True)
	pass
pass

## save result to a file ##
# Result path
result_path ='/home/moraes/Doutorado/Traces/AND/etsi/'
suffix_name = "SpeedxLossRatexDistanceofDiscovery_etsi.csv"
file_name = result_path + suffix_name
SpeedLRDistance_df.to_csv(file_name)
