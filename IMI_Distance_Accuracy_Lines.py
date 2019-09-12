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
#############################################################################################
## FUNCTIONS DEFINITIONS																   ##
#############################################################################################
#-- Function Normalize_values --------------------------------------------------------------#
# Action : Update all values in a column from a dataframe (numeric values only). The first	#
# 	is took as the starting time and all following values are updated accordingly. All		#
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
#-- Function Solution_to_EMU_Time ----------------------------------------------------------#
# Action : Takes a solution data frame (TimeStamp and Neighbors columns) and convert it to  #
#	the time frame of EMU. EMU time is taken as reference and the solution data frame is	#
#	searched in EMU_time +- 0.25 seconds. 													#
# Parameters : 								                                                #
#	- df_ref:	Reference data frame. Usually an EMU data frame 						 	#
# 	- df_sol:	Data frame from solutions with TimeStamp and neighbors columns.				#
# Return : 																		    		#
# 	- df_tmp:	Resulting data frame with TimeStamp and neighbors columns. 					#
#-------------------------------------------------------------------------------------------#
def Solution_to_EMU_Time(df_ref, df_sol):
	## df_ref has the TimeStamp for reference
	
	# Take the list of columns present in the reference data frame.
	columns_in_df_ref = df_ref.columns.values.tolist()
	if 'TimeStamp' in columns_in_df_ref: ## TimeStamp is going to be used in a different way
		columns_in_df_ref.remove('TimeStamp')
	pass

	# Take the list of columns present in the data frame to be converted
	columns_in_df_sol = df_sol.columns.values.tolist()
	if 'TimeStamp' in columns_in_df_sol: ## TimeStamp column is not going to be converted. It is discarded.
		columns_in_df_sol.remove('TimeStamp')
	pass
	
	#print "Reference Columns: ", columns_in_df_ref, "Solution Columns: ", columns_in_df_sol
	##***********************************************************************
	# Creating columns in result data frame
	df_tmp = pd.concat([df_ref,pd.DataFrame(columns=columns_in_df_sol)])
	# Drop not used columns from the reference df
	#print "Columns to be excluded:", columns_in_df_ref
	for column in columns_in_df_ref:
		df_tmp.drop(column, axis=1, inplace=True)
	pass

	## iterating through df rows
	row_idx = df_tmp.index.tolist()	
	for idx in row_idx:
		##For each line in reference df, select solution rows within the time range
		# base time value is equal to EMU time less 0.25 seconds
		base_value = df_tmp.loc[idx,'TimeStamp'] - 250000
		## upper time value is equal to EMU time plus 0.25 seconds
		upper_value = df_tmp.loc[idx,'TimeStamp'] + 250000
		## selecting the corresponding slice in solution's data frame
		df_slice = df_sol[((df_sol['TimeStamp'] >= base_value) & (df_sol['TimeStamp'] < upper_value))]
		## With the sub-dataframe selected, check which columns are present and what action is required
		#print "======================================"
		#print df_slice
		#sys.exit()
		for column in columns_in_df_sol:
			if column == "IMI":
				## 'mean' function has problems with string or NaN values. Using try/catch blocks
				df_slice['IMI'] = pd.to_numeric(df_slice['IMI'], errors='coerce')
				Avg_IMI = df_slice['IMI'].mean()
				#df_tmp.set_value(idx,'IMI', Avg_IMI)
				df_tmp.loc[idx,'IMI'] = Avg_IMI
			elif column == "Latitude":
				df_slice['Latitude'] = pd.to_numeric(df_slice['Latitude'], errors='coerce')
				try:
					Avg_lat = df_slice['Latitude'].mean()
					pass
				except:
					Avg_lat = np.nan
					# Print the error thrown by 'try'
					#traceback.print_exc()
					pass
				df_tmp.loc[idx,'Latitude'] = Avg_lat
			elif column == "Longitude":
				df_slice['Longitude'] = pd.to_numeric(df_slice['Longitude'], errors='coerce')
				try:
					Avg_lon = df_slice['Longitude'].mean()
					pass
				except:
					Avg_lon = np.nan
					pass
				df_tmp.loc[idx,'Longitude'] = Avg_lon
			elif column == "LowerBound":
				df_slice['LowerBound'] = pd.to_numeric(df_slice['LowerBound'], errors='coerce')
				try:
					Avg_lb = df_slice['LowerBound'].mean()
					pass
				except:
					Avg_lb = np.nan
					pass
				df_tmp.loc[idx,'LowerBound'] = Avg_lb
			elif column == "UpperBound":
				df_slice['UpperBound'] = pd.to_numeric(df_slice['UpperBound'], errors='coerce')
				try:
					Avg_ub = df_slice['UpperBound'].mean()
					pass
				except:
					Avg_ub = np.nan
				pass
				df_tmp.loc[idx,'UpperBound'] = Avg_ub
			elif column == "List of Neighbors":
				## With the sub-dataframe selected, it is required check which neighbors are present
				# df_slice might contains more than one row. It is required check each row
				result_list = ""
				slice_index = df_slice.index.tolist()
				for slice_idx in slice_index:
					## Take the neighbor list of each row
					neigh_list = df_slice.loc[slice_idx,'List of Neighbors']
					## Checking whether is it NAN
					try:
						np.isnan(neigh_list)
						pass
					except:
						## Not nan so, it is a list of nodes
						if len(result_list) == 0:
							## if the resulting list is still empty, set to the list of neighbors
							result_list = copy.copy(neigh_list)
							pass
						else:
							## result_list has already a value. Check whether is required add other nodes to it
							# split the list into individual nodes
							nodes = neigh_list.split(';')
							#for node in nodes:
							for node in nodes:
								## check for presence of each node
								if node not in result_list:
									result_list = result_list + node + ';'
								else:
									## already present, ignore it
									continue
								pass
							pass
						pass
					else:
						## empty neighbor list
						continue
					pass
				pass ## end of for slice_idx in slice_index:
				df_tmp.loc[idx,'List of Neighbors'] = result_list
			pass
		pass
	return df_tmp

#-- Function Neighborhood_value_emu --------------------------------------------------------#
# Action : Takes an emu data frame, as it is, and build a new column, named 'Neighbor Value'#
#	with a neighborhood value. This value is calculated by considering neighbors list as 	#
#	binary numbers and then converting it to decimal. As example, consider a data frame from#
#	node v1, with at most 5 neighbors (v2 to v6).											#
#		Time 	 v2 v3 v4 v5 v6	 Neighbor Value												#
#		  t1	  1  0  0  1  0	  		18													#
#		  t2      1  0 	1  0  1   		21				    								#
# Parameters : 								                                                #
#	- df:	Solutions' data frame from Periodic saving process. Without modifications.		#
# Return : 																		    		#
# 	- df_tmp:	A new data frame equals to the first one with the 'Sum' new column. 		#
#-------------------------------------------------------------------------------------------#
def Neighborhood_value_emu(df):
	## Compute the values based on number of nodes
	number_of_nodes = len(List_of_nodes)

	## Temporary dataframes copies
	df_tmp = df.copy()
	nodes_in_df = df_tmp.columns.values.tolist()
	if 'TimeStamp' in nodes_in_df:
		nodes_in_df.remove('TimeStamp')
		df_tmp = df_tmp.set_index('TimeStamp')
		pass
		
	## replacing values
	for index,node in enumerate(List_of_nodes):
		## check for presence of each node
		if node in nodes_in_df:
			neighborhood_value = 0
			## if present, calculate its value
			exp = number_of_nodes - index -1
			neighborhood_value += math.pow(2,exp)
			## replace values in the entire column
			df_tmp[node] = df_tmp[node].replace({1:neighborhood_value})
		else:
			## if not present, continue
			#neighborhood_value += str(0)
			continue
		pass
	pass

	##adding a new column with the sum of other columns (line by line)
	df_tmp['Neighbor Value'] = df_tmp.sum(axis=1)
	df_tmp.fillna(0, inplace=True)
	return df_tmp

#-- Function Compute_Distance --------------------------------------------------------------#
# Action : Compute the distance between two geographical points. The two points are defined	#
# 	by their Latitude and Longitude values. A new column is created with the computed value	#
#	in meters. Data frames passed as parameters are suppose to have the same number of lines#
#	columns entitled Latitude and Longitude and 'TimeStamp'. 								#
# Parameters : 								                                                #
#	- df_01:	data frame one																#
# 	- df_02: 	data frame two 																#
#	- node:		node ID to whom the distance is being computed.								#
# Return : both data frames with an additional column (distance)						    #
#-------------------------------------------------------------------------------------------#
def Compute_Distance(df_01, df_02, node):
	
	#point_02 = df_02[['Latitude', 'Longitude']].astype(float)
	## new columns to hold values
	column_name = 'Distance_' + node
	df_01[column_name] = np.nan
	#df_02[column_name] = np.nan

	## iterating through df rows
	point_01 = []
	point_02 = []
	distance = np.nan
	row_idx = df_01.index.tolist()
	for idx in row_idx:
		try:
			##point 1
			lat_p01 = float(df_01.loc[idx,'Latitude'])
			long_p01 = float(df_01.loc[idx,'Longitude'])
			point_01 = (lat_p01, long_p01)
			##point 2
			lat_p02 = float(df_02.loc[idx,'Latitude'])
			long_p02 = float(df_02.loc[idx,'Longitude'])
			point_02 = (lat_p02, long_p02)
			## computing distance
			distance = vincenty(point_01, point_02).meters
			df_01.loc[idx,column_name] = distance
			#df_02.set_value(idx,column_name,distance)
			pass
		except:
			## catching any error. In this case, set distance do NAN
			#distance = '-' or NAN
			df_01.loc[idx,column_name] = distance
			#df_02.set_value(idx,column_name,distance)
			pass
		else:
			## empty neighbor list
			#distance = 'else'
			df_01.loc[idx,column_name] = distance
			#df_02.set_value(idx,column_name,distance)
			continue
		pass
	pass

	return

#-- Function Accuracy_calculus -------------------------------------------------------------#
# Action : Function to compare two data frames of node neighborhood. Emu data frame and a   #
# 	solution data frame. The process consists in taking the neighborhood information in the	#
# 	solution's data frame and comparing with the same information in EMU's data frame.      #
#   Considering that EMU and each solution are not synchronized, the saving time is slightly#
#   different. This function takes the data in solutions df and compare to the same data in #
#   EMU df saved up to 1 second before. It means that if and_df mention 'n2' as neighbor at #
#	4.35 seconds of test, this data will be searched in emu_df from 3.35 to 4.35 seconds.   #
#   EMU dfs have one column for each node, while solution dfs have only one column, entitled#
#  'List of Neighbors' with all neighbors at a specific time. What is done here is to check #
#   which node's column of EMU df has an 1 as value and searching that node in the list of  #
#   neighbors of the solution df. The final #
#   Accuracy is the number of hits divided by the total number of Emu recognized neighbors  #
#	within a given time slice. A sub-function (Accuracy_value) is used to compare each data #
#	frame line. 																			#
# Parameters : 								                                                #
#	- df_emu: Reference data frame. Often, an EMU data frame is used.						#
# 	- df_sol: Solution data frame to be checked. 											#
# Return:																				    #
#	- new_df: a new data frame witch equals df_sol with an additional Accuracy column. 		#
#-------------------------------------------------------------------------------------------#
def Accuracy_calculus(df_emu, df_sol):
	## Temporary dataframes copies
	df_emu_tmp = df_emu.copy()
	df_emu_tmp = df_emu_tmp.set_index('TimeStamp')

	## Converting EMU df columns in a list. It's supposed to be a list of
	# neighbors but all columns are taken. Check this before using...
	neigh_list = df_emu.columns.values.tolist()
	
	## new column in solution df to hold accuracy values
	column_name = 'DiscoveryAccuracy'
	df_sol[column_name] = np.nan
	## It is not necessary to use more than these two columns
	df_sol_tmp = df_sol[['TimeStamp','List of Neighbors']]	
	
	## write to file for checking reasons
	#df_emu_tmp.to_csv("Emu_check.csv")
	#df_sol_tmp.to_csv("ETSI_check.csv")
	#quit()
	sol_neighbors_row = 0
	## going through EMU data frame row per row
	for index, row in df_emu.iterrows():
		## take the time reference for this row 
		time_ref = row["TimeStamp"]

		## Counters
		neigh_counter = 0
		errors_counter = 0
		
		##For each line in EMU df, select solution rows within the time range:
		## upper time value is equal to EMU time more 0.5 seconds
		upper_value = time_ref + 500000
		## base time value is equal to time_ref
		## cropping solution df rows within the time range
		df_sol_tmp = df_sol[((df_sol['TimeStamp'] >= time_ref) &
						(df_sol['TimeStamp'] <= upper_value))]

		## For each column in EMU df (supposed to be a node)
		for node in neigh_list:
			## check if node is a valid neighbor
			if node in List_of_nodes:
				neigh_counter += 1
				## check the value of node in EMU
				node_value = row[node]
				## Now, taking neighborhood data in solution df
				sol_neigh_list = df_sol_tmp["List of Neighbors"].tolist()
				
				## check if neighbor value in EMU is 1 or 0 (recognized or not)
				if node_value == 0: ## node was not recognized as neighbor by emu
					## check if it was recognized by the solution. 
					# If yes, this is a mistake.
					# I have to search in every item of the list
					for sol_nodes in sol_neigh_list:
						## NaN values generate errors. So, use try
						try:
							present = sol_nodes.find(node)
							pass
						except:
							present = -1
							pass

						if present >= 0:
							# Node present. Error! Not required to search in all list
							errors_counter += 1
							break
						
				elif node_value == 1: ## node was recognized as neighbor
					## Check if it exists in solution df. If yes, ok. Stop the search
					# If not, keep searching till the end of the list. If not found,
					# increment the number of errors
					local_error = 0
					for sol_nodes in sol_neigh_list:
						## NaN values generate errors. So, use try
						try:
							present = sol_nodes.find(node)
							pass
						except:
							present = -1
							pass
						
						if present >= 0:
							## Node present. Ok. Not required to search in all list
							local_error = 0
							break
						else:
							local_error = 1
					pass
					## If an error was found, increase the number of errors
					if local_error == 1:
						errors_counter += 1
						pass
				pass ## end of "node_value == 1"
			pass ## end of "if node in List_of_nodes:"
		pass
		##print ("==== result ====")
		Accuracy = float(neigh_counter - errors_counter) / neigh_counter
		##print ("Nodes: ", neigh_counter, ", Errors: ", errors_counter, "Accuracy: ", Accuracy)
		
		## After checking a line of EMU df, it's required to fill the accuracy
		# result in solution df. The result is written not in one only line but in 
		# all lines of df_sol_tmp
		for sol_idx, sol_row in df_sol_tmp.iterrows():
			ref_TimeStamp = sol_row['TimeStamp']
			df_sol.loc[df_sol['TimeStamp'] == ref_TimeStamp,
				'DiscoveryAccuracy'] = Accuracy
			pass
	pass ## end of "for index, row in df_emu.iterrows():"
	##print (df_sol)
	return df_sol
	
#-- Function Solution_IMI_Line -------------------------------------------------------------#
# Action : Plot a chart with 2 sub-charts each for a different node. Within each sub-chart  #
#	IMI, Lower Bound, Upper Bound and Distance lines are plotted. Yet, over distance lines, #
#	markers are plotted to show when the mentioned nodes were neighbors. Distance lines are #
#   cropped to show distances smaller than a defined value. The legend output is manipulated#
# 	to not show neighborhood markers. 														# 
# Parameters : 								                                                #
#	- df:	a data frame with columns = ['TimeStamp','IMI','LowerBound','UpperBound','List  #
#	of Neighbors','Distance_node'] 															#
# Return : nothing 																		    #
#-------------------------------------------------------------------------------------------#
def Solution_Accuracy_Line( ):
	print ('Building Accuracy Line Charts.')
	#### selecting data for node n1 of Solution 01
	desired_idx = List_of_nodes.index("n1")
	Sol01_TimeStamp = Sol01_Prdsvg_df_list[desired_idx]['TimeStamp'].copy()
	Sol01_Acc = Sol01_Prdsvg_df_list[desired_idx]['DiscoveryAccuracy'].copy()

	#### selecting data for node n1 of Solution 02
	Sol02_TimeStamp = Sol02_Prdsvg_df_list[desired_idx]['TimeStamp'].copy()
	Sol02_Acc = Sol02_Prdsvg_df_list[desired_idx]['DiscoveryAccuracy'].copy()

	# Three subplots sharing both x axis
	f, (ax1, ax2) = plt.subplots(2)
	title = f.suptitle("Bertrand Trace - AND vs ETSI - Node n1 - 10km/h - 15% of loss", fontsize=20)
	f.set_size_inches(23, 10, forward=True)
	title.set_y(0.98)

	###### Solution 01  ###
	ax1.set_title("AND", fontsize=16)
	# building two diff y axes for plotting Delay and Distance
	#ax_Sol01 = [ax1, ax1.twinx()]
	Acc_line = ax1.plot(Sol01_TimeStamp/1000000, Sol01_Acc*100, c='g', lw=2, ls='-', label='Accuracy')	
	
	# formating y axis to show Delay Value Variation
	ax1.set_ylabel('AND Accuracy (%)', color='b', fontsize=15)
	#ax1.yaxis.set_ticks(np.arange(0, 103, 10))
	#ax1.set_ylim(0, 103)
	## arranging X axis
	#ax1.xaxis.set_ticks(np.arange(20, 101, 5))	
	#ax1.set_xlim(20, 100)
	
	###### Solution 02  ###
	ax2.set_title("ETSI", fontsize=16)
	# building two diff y axes for plotting Delay and Distance
	#ax_Sol02 = [ax2, ax2.twinx()]
	Acc_line = ax2.plot(Sol02_TimeStamp/1000000, Sol02_Acc*100, c='g', lw=2, ls='-', label='Accuracy')	
		
	# formating y axis to show Delay Value Variation
	ax2.set_ylabel('ETSI Accuracy (%)', color='b', fontsize=15)
	#ax2.yaxis.set_ticks(np.arange(0, 103, 10))
	#ax2.set_ylim(0, 103)

	## arranging X axis
	#ax2.xaxis.set_ticks(np.arange(20, 101, 5))
	ax2.set_xlabel('Time', fontsize=17)
	#ax2.xaxis.set_label_coords(0.98, -0.05)
	#ax2.set_xlim(20, 100)
	
	ax1.grid(True)
	ax2.grid(True)

	#### legends ##
	# first chart
	lines = ax1.get_lines()
	ax1.legend(lines, [line.get_label() for line in lines], loc='lower right', fontsize=16)
	# second chart
	lines_02 = ax2.get_lines()
	ax2.legend(lines_02, [line.get_label() for line in lines_02], loc='lower right',fontsize=16)
	
	return

#-- Function Solution_Discovery_Distance_Lines_v1 ------------------------------------------#
# Action : Plot a chart with 2 sub-charts each for a different solution (AND, ETSI). Within #
#	each sub-chart, Distance lines are plotted. Yet, a constant line at value of 200 meters #
#	is plotted to highlight the communication range value and a line at the value of the    #
# 	safety distance (2seconds of movement at an specified speed).  							#
#   Distance lines are cropped to show distances smaller than a defined value. The legend   #
# 	output is manipulated to not show all neighborhood markers.								# 
# Parameters : 								                                                #
#	- No parameters. This procedure access global data frames								#
# Return : nothing 																		    #
#-------------------------------------------------------------------------------------------#
def Solution_Discovery_Distance_Lines_n1( ):
	print ('Building Line Charts.')
	#### selecting data for node n1 of Solution 01
	desired_idx = List_of_nodes.index("n1")
	Sol01_TimeStamp = Sol01_Prdsvg_df_list[desired_idx]['TimeStamp'].copy()

	## n1 distance to neighbors.
	## I have twenty nodes, but i'm using only the distance to the moving ones (n*)
	Sol01_OthersDist = {}
	Sol01_DistHighlight = {}
	for node in List_of_moving_nodes:
		if node != 'n1':
			column_name = 'Distance_' + node
			#Sol01_OthersDist[node] = Sol01_Prdsvg_df_list[desired_idx][column_name].apply(Till_250)
			Sol01_OthersDist[node] = Sol01_Prdsvg_df_list[desired_idx][column_name]
			## Taking distance values only where there is neighborhood relation
			tmp_df = Sol01_Prdsvg_df_list[desired_idx][['TimeStamp','List of Neighbors',column_name]]
			## some lines have 'nan' as value which makes str.contains impossible
			tmp_df['List of Neighbors'].fillna('-', inplace = True)
			Sol01_DistHighlight[node] = tmp_df[tmp_df['List of Neighbors'].str.contains(node)]
		pass
	pass
	
	## ******************************************************************** ##
	Sol02_TimeStamp = Sol02_Prdsvg_df_list[desired_idx]['TimeStamp'].copy()
	
	## Plotting distance to nodes.
	Sol02_OthersDist = {}
	Sol02_DistHighlight = {}
	for node in List_of_moving_nodes:
		if node != 'n1':
			column_name = 'Distance_' + node
			Sol02_OthersDist[node] = Sol02_Prdsvg_df_list[desired_idx][column_name]
			#print (node, Sol02_OthersDist[node])
			## Taking distance values only where there is neighborhood relation and saving in a
			# second dataframe to highlight the neighborhood relation
			tmp_df = Sol02_Prdsvg_df_list[desired_idx][['TimeStamp','List of Neighbors',column_name]]
			tmp_df['List of Neighbors'].fillna('-', inplace = True)
			Sol02_DistHighlight[node] = tmp_df[tmp_df['List of Neighbors'].str.contains(node)]		
			#print (node, Sol02_DistHighlight[node])
			#quit()
		pass
	pass

	# Two subplots sharing x axis
	f, (ax1, ax2) = plt.subplots(2)
	title = f.suptitle("Bertrand Trace - AND vs ETSI Distance of Discovery - Node n1 - 10km/h - 15% of loss", fontsize=20)
	f.set_size_inches(23, 10, forward=True)
	#title.set_y(0.98)

	###### Node n1 - Solution 01 ###
	ax1.set_title("AND", fontsize=18)
	# building two diff y axes for plotting Delay and Distance

	## Plotting Distance lines. Distances from n1 to n2, n3 and n4
	# In case of too many nodes, dropping some of them to not polute too much the chart
	node_neighbors = copy.copy(List_of_moving_nodes)
	for idx, node in enumerate(node_neighbors):
		#print (idx, node)
		if node != 'n1':
			label = 'Distance to ' + node
			color = cm.Greens((idx + 1) * 75)
			## distance line
			line = Sol01_OthersDist[node]
			Dist_line = ax1.plot(Sol01_TimeStamp/1000000, line, c=color, lw=2, ls='--',label=label)
			## highlighting neighborhood characteristic
			# taking one of twenty elements in all array (diminishing the number of nodes)
			Node_df = Sol01_DistHighlight[node]
			xvalues = Node_df['TimeStamp']
			column_name = 'Distance_' + node
			highlight_line = Node_df[column_name]
			ax1.plot(xvalues/1000000, highlight_line, c=color, ls='none', 
				marker='o', markersize=6, label='neighborhood')
		pass
	pass

	## Reference line of communication range (200 meters)
	ax1.axhline(y=200,xmin=0,xmax=25,c="blue",linewidth=2,zorder=0,label='Comm. Range')
	## Safety line (equals the distance travelled in 2 seconds)
	speed1 = 30 # speed in km/h (one vehicle)
	speed2 = 30 # speed in km/h (another vehicle)
	# computing the safety line (sl) considering two vehicles.
	# transform in meters per second and multiply by 2 seconds
	sl = ((speed1 + speed2)/3.6) * 2
	## Plotting
	ax1.axhline(y=sl,xmin=0,xmax=25,c="red",linewidth=2,zorder=0, label='Safety Distance')

	# formating y axis to show Distance between nodes variation
	#ax_Sol01[1].set_ylabel('Distances to other nodes (m)', color='g', fontsize=16)
	#ax1.yaxis.set_ticks(np.arange(0, 250, 20))
	#ax1.set_ylim(0, 250)
	###### Arranging X axis for the second chart ####
	#start, end = ax2.get_xlim()
	#ax1.xaxis.set_ticks(np.arange(30, 101, 2))
	#ax1.set_xlim(30,100)

	###### Solution 02  ###
	ax2.set_title("ETSI", fontsize=18)

	## Plotting Distance lines. Distances from v1 to v2, v3 and v4
	# In case of too many nodes, dropping some of them to not polute too much the chart
	node_neighbors = copy.copy(List_of_moving_nodes)
	for idx, node in enumerate(node_neighbors):
		if node != 'n1':
			label = 'Distance to ' + node
			color = cm.Greens((idx + 1) * 75)
			line = Sol02_OthersDist[node]
			Dist_line = ax2.plot(Sol02_TimeStamp/1000000, line, c=color, lw=2, ls='--', label=label)
			## highlighting neighborhood characteristic
			# taking one of twenty elements in all array (diminishing the number of nodes)
			Node_df = Sol02_DistHighlight[node]
			xvalues = Node_df['TimeStamp']
			column_name = 'Distance_' + node
			highlight_line = Node_df[column_name]
			ax2.plot(xvalues/1000000, highlight_line, c=color, ls='none', 
				marker='o', markersize=6, label='neighborhood')
		pass
	pass
	
	## Reference line of communication range (200 meters)
	ax2.axhline(y=200,xmin=0,xmax=25,c="blue",linewidth=2,zorder=0,label='Comm. Range')
	## Safety line (equals the distance travelled in 2 seconds)
	ax2.axhline(y=sl,xmin=0,xmax=25,c="red",linewidth=2,zorder=0, label='Safety Distance')

	# formating y axis to show Distance between nodes variation
	ax2.set_ylabel('Distances to other nodes (m)', fontsize=16)
	#ax2.yaxis.set_ticks(np.arange(0, 250, 20))
	#ax2.set_ylim(0, 250)

	
	###### Arranging X axis for the second chart ####
	#start, end = ax2.get_xlim()
	#ax2.xaxis.set_ticks(np.arange(30, 101, 2))
	ax2.set_xlabel('Time', fontsize=17)
	#ax2.xaxis.set_label_coords(0.98, -0.05)
	#ax2.set_xlim(30,100)
	
	ax1.grid(True)
	ax2.grid(True)
	
	#### legends ##
	## Eliminate some lines (legend is too big). First chart.
	chart1_handles, chart1_labels = ax1.get_legend_handles_labels()
	## cropping undesired legends
	chart1_handle_list, chart1_label_list = [], []
	for handle, label in zip(chart1_handles, chart1_labels):
		#print label
		if "neighborhood" not in label:
			chart1_handle_list.append(handle)
			chart1_label_list.append(label)
		pass
	pass
	ax1.legend(chart1_handle_list, chart1_label_list, loc='lower left',fontsize=12)

	## Eliminate some lines (legend is too big). Second chart.
	chart2_handles, chart2_labels = ax2.get_legend_handles_labels()
	## cropping undesired legends
	chart2_handle_list, chart2_label_list = [], []
	for handle, label in zip(chart2_handles, chart2_labels):
		#print label
		if "neighborhood" not in label:
			chart2_handle_list.append(handle)
			chart2_label_list.append(label)
		pass
	pass
	ax2.legend(chart2_handle_list, chart2_label_list, loc='lower left',fontsize=12)

	## Adding a second legend
	#legend2 = 
	
	return
#############################################################################################
## General Script
## Emu is used as reference to the other solutions. That's why its traces must be treated
## first. Later, Solutions' data frames will be constructed with Emu's TimeStamp values
# main path of trace files
start_path ='/home/moraes/Doutorado/Traces'

#############################################################################################
###### EMU's traces processing for AND, 30km, lr-0 #######
print ("EMU's traces processing for Solution 01 - AND, 10kmh, lr-15")
EMU_Sol01_Final_path = start_path + '/Bertrand/resultats-demo-and-n31-a1-CompleteScene-10kmh-and-lr15/emu/'
## A .csv file for each node
filenames = glob.glob(EMU_Sol01_Final_path + "*.csv")
## sorting in alphabetic order
filenames.sort()

## Files were already processed or not
done = 0

EMU_Sol01_df_list = []
EMU_Sol01_Crop_df_list = []
## Processing one file at a time
for filename in filenames: 	## Basic Data Frame format: TimeStamp	v1 	v2 	v3 	...
	## Since the process take too long, if it was done once, it's not required to do it again
	try:
		## check if processed files exist
		## already processed file
		EMU_file_name = filename + '.done'
		EMU_Sol01_Crop_df_list.append(pd.read_csv(EMU_file_name))
		print ("===", filename, " already processed.. keep going =====")
		## Processed
		done = 1
		pass
	except:	
		print ("===", filename, " not processed.. doing =====")
		## Reading files for processing
		EMU_Sol01_df_list.append(pd.read_csv(filename))
		## Not processed yet
		done = 0
		pass
pass

## Further process or not
if done == 0:
	## Discarding first 2 seconds of experiments. This is interesting because
	# EMU starts saving data before Solutions and the system takes time to stabilize
	for df in EMU_Sol01_df_list:
		for col in df.columns:
			if 'Unnamed' in col:
				del df[col] # For some reason, an unnamed column is being generated. Now, discarding it.
			pass
		pass
		start_value = df['TimeStamp'].min()
		last_value = start_value + 20000000
		tmp = df[((df['TimeStamp'] >= start_value) & (df['TimeStamp'] < last_value))]
		row_indexes = tmp.index.tolist()
		EMU_Sol01_Crop_df_list.append(df.drop(df.index[[row_indexes]])) 	## Cropping out the first 2 seconds of test
	pass

	## After processing, save the resulting dfs to files
	df_index = -1
	for filename in filenames:
		df_index += 1
		Save_file_name = filename + '.done'
		EMU_Sol01_Crop_df_list[df_index].to_csv(Save_file_name)
	pass
pass


######################################################
###### EMU's traces processing for ETSI, 10kmh, lr-0 #######
print ("EMU's traces processing for Solution 02 - ETSI, 10kmh, lr-15")
EMU_Sol02_Final_path = start_path + '/EMU/etsi/10kmh/lr-15/'
filenames = glob.glob(EMU_Sol02_Final_path + "*.csv")
## sorting in alphabetic order
filenames.sort()

## Files were already processed or not
done = 0

EMU_Sol02_df_list = []
EMU_Sol02_Crop_df_list = []
## Processing one file at a time
for filename in filenames: 	## Basic Data Frame format: TimeStamp	v1 	v2 	v3 	...
	## Since the process take too long, if it was done once, it's not required to do it again
	try:
		## check if processed files exist
		## already processed file
		EMU_file_name = filename + '.done'
		EMU_Sol02_Crop_df_list.append(pd.read_csv(EMU_file_name))
		print ("===", filename, " already processed.. keep going =====")
		## Processed
		done = 1
		pass
	except:	
		print ("===", filename, " not processed.. doing =====")
		## Reading files for processing
		EMU_Sol02_df_list.append(pd.read_csv(filename))
		## Not processed yet
		done = 0
		pass
pass

## Further process or not
if done == 0:
	## Discarding first 2 seconds of experiments. This is interesting because
	# EMU starts saving data before Solutions and the system takes time to stabilize
	for df in EMU_Sol02_df_list:
		for col in df.columns:
			if 'Unnamed' in col:
				del df[col] # For some reason, an unnamed column is being generated. Now, discarding it.
			pass
		pass
		start_value = df['TimeStamp'].min()
		last_value = start_value + 20000000
		tmp = df[((df['TimeStamp'] >= start_value) & (df['TimeStamp'] < last_value))]
		row_indexes = tmp.index.tolist()
		EMU_Sol02_Crop_df_list.append(df.drop(df.index[[row_indexes]])) 	## Cropping out the first 2 seconds of test
	pass

	## After processing, save the resulting dfs to files
	df_index = -1
	for filename in filenames:
		df_index += 1
		Save_file_name = filename + '.done'
		EMU_Sol02_Crop_df_list[df_index].to_csv(Save_file_name)
	pass
pass

################################################################################################
## Solutions' traces processing 															  ##
## The idea is to use EMU related saved data as reference for the solutions' data. 			  ##
## EMU timing is the reference for all results (accuracy, average IMI, average distance, etc).##
## Setting all data frames to EMU time-reference. Computing average or repeating values when  ##
## required. 																				  ##
################################################################################################
######## Solution 01 ###########
print ("==========================================")
print ("Solutions_01 traces processing - AND, 10kmh, lr-15")
Sol01_path = start_path + '/Bertrand/resultats-demo-and-n31-a1-CompleteScene-10kmh-and-lr15/and/'
## From periodic-saved trace taking list of neighbors, Upper bound and Lower Bound
Sol01_prdsvg_msg_files = glob.glob(Sol01_path + "*.Periodic.csv")
## From sent-messages trace take IMI
Sol01_sent_msg_files = glob.glob(Sol01_path + "*.Sent_Messages.csv")
## sorting in alphabetic order
Sol01_prdsvg_msg_files.sort()
Sol01_sent_msg_files.sort()

### Files were already processed or not ###
## Lists of data frames indexed in alphabetical order of nodes' names.
## so, [1] = al1; [2] = al2... check list_of_nodes for other names
Sol01_Sent_df_list_tmp = []
Sol01_Sent_df_list = []
Sol01_Number_Sent_Msg_list = []

## ==== Processing Sent_Msgs files ==== ##
# It's required to process on file per node
done = len(List_of_nodes)
for filename in Sol01_sent_msg_files:
	## Since the process take too long, if it was done once, it's not required to do it again
	try:
		## check if processed files exist
		## already processed file
		Sol01_file_name = filename + '.done'
		Sol01_Number_Sent_Msg_list.append(pd.read_csv(Sol01_file_name))
		print ("===", filename, " already processed.. keep going =====")
		done -= 1
		pass
	except:
		print ("===", filename, " not processed yet.. doing =====")
		## Reading traces
		Sol01_Sent_df_list_tmp.append(pd.read_csv(filename))
		pass
pass

## Further process for Sent Messages or not
if done > 0:
	for df in Sol01_Sent_df_list_tmp:
		## Taking the biggest Sequence Number of Sent Messages. 
		#It equals the number of sent messages!
		Sol01_Number_Sent_Msg_list.append(df['Seq. Number'].max())
		## taking off IMI values out of the range. 
		#Usually the first IMI value is not correct
		df = df[df.IMI < 10000]
		## crop out other values
		Sol01_Sent_df_list.append(
			df[['TimeStamp', 'Latitude', 'Longitude', 'IMI']].copy())
	pass

 	## After processing, save the resulting dfs to files
	df_index = -1
	for filename in Sol01_sent_msg_files:
		df_index += 1
		Sol01_file_name = filename + '.done'
		print ("saving file: ", Sol01_file_name)
		Sol01_Sent_df_list[df_index].to_csv(Sol01_file_name)
	pass
pass

### Files for Periodic savings were already processed or not ###
Sol01_Overall_Accuracy_Avg_list = []
Sol01_Prdsvg_df_list_tmp = []
Sol01_Prdsvg_df_list = []

## ==== Processing Periodic_saved_msgs files ==== ##
# It's required to process one file per node
done = len(List_of_nodes)
for filename in Sol01_prdsvg_msg_files:
	## Since the process take too long, if it was done once, 
	#it's not required to do it again
	try:
		## check if processed files exist
		## already processed file for Periodic messages
		Sol01_file_name = filename + '.done'
		Sol01_Prdsvg_df_list.append(pd.read_csv(Sol01_file_name))
		print ("===", filename, " already processed.. keep going =====")
		done -= 1 # one less file to process
		pass
	except:
		print ("===", filename, " not processed yet.. doing ====="	)
		## Reading traces
		Sol01_Prdsvg_df_list_tmp.append(pd.read_csv(filename))
		pass
pass

## Further process for Periodic savings or not
if done > 0:
	## First data format steps.
	for df in Sol01_Prdsvg_df_list_tmp:
		## Replacing '-' values by 'not a number'
		df.replace('-', np.nan, inplace=True)
		##Copying only interested columns.
		Sol01_Prdsvg_df_list.append(df[['TimeStamp','List of Neighbors','LowerBound',
			'UpperBound','IMI','Latitude','Longitude']].copy())
	pass

	## Computing distance between n1 and all other nodes. The result is saved
	# in a 'Distance_node' new column. All calculus are performed with Periodic
	#saved traces.
	############## check distance computation!!! ###################
	desired_idx = List_of_nodes.index("n1")
	for index,node in enumerate(List_of_nodes):
		if node != "n1": # Impossible to compute node's distance to itself
			## Computing distance between 'n1' and all other moving nodes
			if node in List_of_moving_nodes: 
				## parameter 'node' is used to know to which node the distance is being computed
				Compute_Distance(Sol01_Prdsvg_df_list[desired_idx], 
					Sol01_Prdsvg_df_list[index], node)
			pass
		pass
	pass
	
	## Last metric to be computed is the Accuracy. 
 	# Using EMU df as reference and Solution_Prdsvg df.
	Sol01_Accuracy_df_list = []
	Sol01_Overall_Accuracy_Avg_list = []
	#print ("EMU DF itens", len(EMU_Sol01_Crop_df_list))
	#print ("Sol DF itens", len(Sol01_Prdsvg_df_list))
	for idx,node in enumerate(List_of_nodes):
		#print ("accuracy:", idx, node)
		Accuracy_calculus(EMU_Sol01_Crop_df_list[idx],Sol01_Prdsvg_df_list[idx])
	pass

	## Now, after all other calculus, It is possible to Normalize TimeStamp value
	for df in Sol01_Prdsvg_df_list:
		Normalize_values(df, 'TimeStamp')
	pass

	### Save processed data frames in files
	df_index = -1
	for filename in Sol01_prdsvg_msg_files:
		df_index += 1
		Sol01_file_name = filename + '.done'
		print ("saving files: ", Sol01_file_name)
		Sol01_Prdsvg_df_list[df_index].to_csv(Sol01_file_name)
	pass
pass

################################
######## Solution 02 ###########
print ("==========================================")
print ("Solution_02 traces processing, ETSI, 10kmh, lr-15")
Sol02_path = start_path + '/AND/etsi/10kmh/lr-15/'
## From periodic-saved trace taking list of neighbors, Upper bound and Lower Bound
Sol02_prdsvg_msg_files = glob.glob(Sol02_path + "*.Periodic.csv")
## From sent-messages trace take IMI
Sol02_sent_msg_files = glob.glob(Sol02_path + "*.Sent_Messages.csv")
## sorting in alphabetic order
Sol02_prdsvg_msg_files.sort()
Sol02_sent_msg_files.sort()

### Files were already processed or not ###
## Lists of data frames indexed in alphabetical order of nodes' names.
## so, [1] = al1; [2] = al2... check list_of_nodes for other names
Sol02_Sent_df_list_tmp = []
Sol02_Sent_df_list = []
Sol02_Number_Sent_Msg_list = []

## ==== Processing Sent_Msgs files ==== ##
# It's required to process on file per node
done = len(List_of_nodes)
for filename in Sol02_sent_msg_files:
	## Since the process take too long, if it was done once, it's not required to do it again
	try:
		## check if processed files exist
		## already processed file
		Sol02_file_name = filename + '.done'
		Sol02_Number_Sent_Msg_list.append(pd.read_csv(Sol02_file_name))
		print ("===", filename, " already processed.. keep going =====")
		done -= 1
		pass
	except:
		print ("===", filename, " not processed yet.. doing =====")
		## Reading traces
		Sol02_Sent_df_list_tmp.append(pd.read_csv(filename))
		pass
pass

## Further process for Sent Messages or not
if done > 0:
	for df in Sol02_Sent_df_list_tmp:
		## Taking the biggest Sequence Number of Sent Messages. 
		#It equals the number of sent messages!
		Sol02_Number_Sent_Msg_list.append(df['Seq. Number'].max())
		## taking off IMI values out of the range. 
		#Usually the first IMI value is not correct
		df = df[df.IMI < 10000]
		## crop out other values
		Sol02_Sent_df_list.append(
			df[['TimeStamp', 'Latitude', 'Longitude', 'IMI']].copy())
	pass

	## After processing, save the resulting dfs to files
	df_index = -1
	for filename in Sol02_sent_msg_files:
		df_index += 1
		Sol02_file_name = filename + '.done'
		print ("saving file: ", Sol02_file_name)
		Sol02_Sent_df_list[df_index].to_csv(Sol02_file_name)
	pass
pass

### Files for Periodic savings were already processed or not ###
Sol02_Overall_Accuracy_Avg_list = []
Sol02_Prdsvg_df_list_tmp = []
Sol02_Prdsvg_df_list = []

## ==== Processing Periodic_saved_msgs files ==== ##
# It's required to process on file per node
done = len(List_of_nodes)
for filename in Sol02_prdsvg_msg_files:
	## Since the process take too long, if it was done once, 
	#it's not required to do it again
	try:
		## check if processed files exist
		## already processed file for Periodic messages
		Sol02_file_name = filename + '.done'
		Sol02_Prdsvg_df_list.append(pd.read_csv(Sol02_file_name))
		print ("===", filename, " already processed.. keep going =====")
		done -= 1 # one less file to process
		pass
	except:
		print ("===", filename, " not processed yet.. doing ====="	)
		## Reading traces
		Sol02_Prdsvg_df_list_tmp.append(pd.read_csv(filename))
		pass
pass

## Further process for Periodic savings or not
if done > 0:
	## First data format steps.
	for df in Sol02_Prdsvg_df_list_tmp:
		## Replacing '-' values by 'not a number'
		df.replace('-', np.nan, inplace=True)
		##Copying only interested columns.
		Sol02_Prdsvg_df_list.append(df[['TimeStamp','List of Neighbors','LowerBound',
			'UpperBound','IMI','Latitude','Longitude']].copy())
	pass

	## Computing distance between n1 and all other nodes. The result is saved
	# in a 'Distance_node' new column. All calculus are performed with Periodic
	#saved traces.
	############## check distance computation!!! ###################
	desired_idx = List_of_nodes.index("n1")
	for index,node in enumerate(List_of_nodes):
		if node != "n1": # Impossible to compute node's distance to itself
			## Computing distance between 'n1' and all other moving nodes
			if node in List_of_moving_nodes: 
				## parameter 'node' is used to know to which node the distance is being computed
				Compute_Distance(Sol02_Prdsvg_df_list[desired_idx], 
					Sol02_Prdsvg_df_list[index], node)
				#print ">>> Distance from n1=", desired_idx, " to ", node, "=", index, " <<<<"			
			pass
		pass
	pass
	
	## Last metric to be computed is the Accuracy. 
	# Using EMU df as reference and Solution_Prdsvg df.
	Sol02_Accuracy_df_list = []
	Sol02_Overall_Accuracy_Avg_list = []
	for idx,node in enumerate(List_of_nodes):
		##print ("Computing accuracy for ",node,":")
		Accuracy_calculus(EMU_Sol02_Crop_df_list[idx],Sol02_Prdsvg_df_list[idx])
	pass

	## Now, after all other calculus, It is possible to Normalize TimeStamp value
	## I'M NOT SURE I HAVE TO NORMALIZE
	for df in Sol02_Prdsvg_df_list:
		Normalize_values(df, 'TimeStamp')
	pass

	### Save processed data frames in files
	df_index = -1
	for filename in Sol02_prdsvg_msg_files:
		df_index += 1
		Sol02_file_name = filename + '.done'
		print ("saving files: ", Sol02_file_name)
		Sol02_Prdsvg_df_list[df_index].to_csv(Sol02_file_name)
	pass
pass

print ("bora pros graficos???")
#############################################################################################
## BUILDING CHARTS  																	   ##
#############################################################################################
## Charts path
charts_path ='/home/moraes/Doutorado/Charts/NewExperiments/'
#### Accuracy Charts
Solution_Accuracy_Line()
suffix_name = "Testing-Bertrand-Trace-Accuracy-10kmh-lr-15-2019-3-29.png"
file_name = charts_path + suffix_name
plb.savefig(file_name)
##### Distance_of_discovery charts
Solution_Discovery_Distance_Lines_n1()
suffix_name = "Testing-Bertrand-Trace-Discovery_Distance_Lines-10kmh-lr-15-2019-3-29.png"
file_name = charts_path + suffix_name
plb.savefig(file_name)

plt.show()