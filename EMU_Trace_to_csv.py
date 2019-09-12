#!/usr/bin/python3

#### Converting files from this format
#06/11/2018:11h02m44s:1528707764356919:1528707764356:n1;al1 al2 al3:n2;al1 al7 al8 ap1 ap2 ap3
#### To files of this format for each node
#TimeStamp,n1,n2,al1,al2,al3,al7,al8,ap1,ap2,ap3
#1528707764356919,1,0,1,1,1
#1435756245460180,1,1,0,0,1
#1435756246476204,1,0,0,1,1

from sys import argv
import glob
import sys
import re
import pandas as pd
import numpy as np

##List of nodes
# Take care about two nodes with similar names like 'v1' and 'v10'. One might be counted as the other.
List_of_nodes = ['n1','n2','n3','n4','al1','al2','al3','al4','al5','al6','al7','al8',
				'ap1','ap2','ap3','ap4','ap5','ap6','ap7','ap8']

## List of data frames to receive each kind of saving process: 
#received messages; sent messages; periodic saved messages
df_list = {}
possible_neigh = {}
dictionary_keys = {}
dictionary_values = {}
insert_values = {}

##---------------------------------------------------------------------------------------------##
## General Script 																			   ##
##---------------------------------------------------------------------------------------------## 
## command line parameters
script, path, filemask = argv

files = path + filemask
filenames = sorted(glob.glob(files))

#print filemask
#print filenames
#sys.exit()

for f in filenames:
	## opening file
	and_trace = open(f)

	for line in and_trace:
		## Comparing with the pattern
		###06/11/2018:11h02m44s:1528707764356919:1528707764356:n1;al1 al2 al3 al4 al5 al6 al7 ap1 ap2 ap3 ap4
		###ap5 ap6 ap7 ap8:n2;al1 al2 al3 al4 al5 al6 al7 al8 ap1 ap2 ap3 ap4 ap5 ap6 ap7 ap8 n3 n4
		matchObj = re.match(r'(.*):(.*):([0-9]*):([0-9]*):(.*)',line)
		if matchObj:
			saving_time = matchObj.group(3)
			gen_string = matchObj.group(5)
			## saving time-registered and detaching the general message. Next, process
			# the general string with the list of neighbors and the list of lossrates
			if len(gen_string) > 0:
				##break the entire list in lists of neighbors for each node: n2;al1 al2 al3 al4
				substrings = gen_string.split(":")
				for substring in substrings:
					## Break the list node; neighbors in owner and neighbors
					list_neighbors = substring.split(";")
					owner = list_neighbors[0]
					neighbors = list_neighbors[1]
					#print "Owner: ", owner, "Neighbors: ", neighbors
					if owner in List_of_nodes:
						## create a separate data frame for each owner
						try:
							## a silly statement to check data frame existence
							# before create, check whether data frame already exists
							exist = df_list[owner]
						except KeyError:
							## data frame doesn't exist, create it
							possible_neigh[owner] = list(List_of_nodes)
							## remove the owner of the list
							possible_neigh[owner].remove(owner)
							columns = list(possible_neigh[owner])
							columns.insert(0,'TimeStamp')
							new_df = pd.DataFrame(data=np.zeros((0,len(columns))), columns=columns)
							df_list[owner] = new_df
							# dictionary to insert values
							dictionary_keys[owner] = list(columns)
							dictionary_values[owner] = list(columns)
						pass
						## Data frame created, filling
						# There will always exist a column with a TimeStamp
						dictionary_values[owner][0] = saving_time
						## check the presence of each possible neighbor
						for node in possible_neigh[owner]:
							index = dictionary_keys[owner].index(node)
							if node in list_neighbors[1]:
								dictionary_values[owner][index] = 1
							else:
								dictionary_values[owner][index] = 0
							pass
						pass
						#merging keys and values
						insert_values[owner] = dict(zip(dictionary_keys[owner], dictionary_values[owner]))	
						df_list[owner].loc[len(df_list[owner])] = insert_values[owner]
					pass
				pass ## end of "if 'neighbors' in substring"
			pass ## end of "for substring in substrings"
		pass
		print ("Line doesn't match")
	pass ## end of "for line in and_trace:"
pass

## Writing data frames to files
for node in List_of_nodes:
	#creating files in the same directory as the sources
	result_filename = path + 'Neighbors-' + node + '.csv'
	## It might happens that a node didn't received any message, or didn't sent any messages. In these cases,
	# an attempt to save files using these "traces" will generate an error. So, use "try" construction
	try:
		df_list[node].to_csv(result_filename)
	except Exception as e:
		print (e)
	pass
pass
