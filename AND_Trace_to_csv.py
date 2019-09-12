#!/usr/bin/python3
## Tested in July 2019, this python program convert AND traces into separated csv files. It creates 3
# resulting files (received messages; sent messages; periodic saved messages). It works regardless the 
# number of nodes. Yet, it can be called from a unique folder to create output files in the same folder
# of the source files.
from sys import argv
import os
import re
import glob
import pandas as pd
import numpy as np


##------------------- ##
## Required data      ##
##------------------- ##
List_of_algorithms = ['and','etsi']
List_of_speeds = ['10kmh','30kmh','50kmh','70kmh','90kmh']
List_of_LossRates = ['lr0','lr15','lr30','lr45','lr60','lr75','lr90']
List_of_nodes = ['n1','n2','n3','n4','al1','al2','al3','al4','al5','al6','al7','al8',
				'ap1','ap2','ap3','ap4','ap5','ap6','ap7','ap8']
## List of trace messages
List_of_traces = ['Received_Messages','Sent_Messages','Periodic']

##---------------------------------------------------------------------------------------------##
## Received messages processing function													   ##
##---------------------------------------------------------------------------------------------##
def Received_msg_process(message):
	## Received messages pattern
	result = {'Sending Node(SN)':'','IMI':'','Net_Reli':'','Address of SN':'','Latitude':'','Longitude':'',
			'Altitude':'','Speed':'','Heading':'','Seq. Number':'','List of Neighbors':'','Payload':''}

	## Break message into smaller pieces. Using regular expressions again
	#^andis~v3^anddel~556^andrel~1.0^andadr~172.17.160.20^lat~49.6697989608^lon~2.76979156054
	#^alt~86.125^vit~0.0^hea~0.0^andsn~141^andneigh~v2;v6;v7;v8;v4;v1;v10;v9;v5;^andpl~v3 says: I'm here!^"
	small_pieces = re.match(r'.*\^andis~(.*)\^anddel~([0-9]*)\^andrel~([0-9]*.[0-9]*)\^andadr~(.*)\^lat~([0-9]*.[0-9]*)\^lon~([0-9]*.[0-9]*)\^alt~([0-9]*.[0-9]*)\^vit~([0-9]*.[0-9]*)\^hea~(.*)\^andsn~([0-9]+)\^andneigh~(.*)\^andpl~(.*)\^.*',message)
	if small_pieces:
		result['Sending Node(SN)'] = small_pieces.group(1)
		result['IMI'] = small_pieces.group(2)
		result['Net_Reli'] = small_pieces.group(3)
		result['Address of SN'] = small_pieces.group(4)
		result['Latitude'] = small_pieces.group(5)
		result['Longitude'] = small_pieces.group(6)
		result['Altitude'] = small_pieces.group(7)
		result['Speed'] = small_pieces.group(8)
		result['Heading'] = small_pieces.group(9)
		result['Seq. Number'] = small_pieces.group(10)
		result['List of Neighbors'] = small_pieces.group(11)
		result['Payload'] = small_pieces.group(12)
	else:
		print ("::Received message didn't match::")
		print (message)
	pass
	return result
##---------------------------------------------------------------------------------------------##
## Sent messages processing function														   ##
##---------------------------------------------------------------------------------------------##
def Sent_msg_process(message):
	## Sent messages pattern
	result = {'Sending Node(SN)':'','IMI':'','Net_Reli':'','Address of SN':'','Latitude':'','Longitude':'',
			'Altitude':'','Speed':'','Heading':'','Seq. Number':'','List of Neighbors':'','Payload':''}

	## Break message into smaller pieces. Using regular expressions again
	# ^andis~v9^anddel~556^andrel~1.0^andadr~172.17.160.20^lat~49.6695677095^lon~2.76969343804^alt~85.675
	#^vit~0.0^hea~0.0^andsn~139^andneigh~v6;v2;v7;v3;v8;v4;v1;v5;v10;^andpl~v9 says: I'm here!^"
	small_pieces = re.match(r'.*\^andis~(.*)\^anddel~([0-9]*)\^andrel~([0-9]*.[0-9]*)\^andadr~(.*)\^lat~([0-9]*.[0-9]*)\^lon~([0-9]*.[0-9]*)\^alt~([0-9]*.[0-9]*)\^vit~([0-9]*.[0-9]*)\^hea~(.*)\^andsn~([0-9]+)\^andneigh~(.*)\^andpl~(.*)\^.*',message)
	if small_pieces:
		result['Sending Node(SN)'] = small_pieces.group(1)
		result['IMI'] = small_pieces.group(2)
		result['Net_Reli'] = small_pieces.group(3)
		result['Address of SN'] = small_pieces.group(4)
		result['Latitude'] = small_pieces.group(5)
		result['Longitude'] = small_pieces.group(6)
		result['Altitude'] = small_pieces.group(7)
		result['Speed'] = small_pieces.group(8)
		result['Heading'] = small_pieces.group(9)
		result['Seq. Number'] = small_pieces.group(10)
		result['List of Neighbors'] = small_pieces.group(11)
		result['Payload'] = small_pieces.group(12)
	else:
		print ("::Sent Message didn't match::")
		print (message)
	pass
	return result
##---------------------------------------------------------------------------------------------##
## Periodic messages processing function													   ##
##---------------------------------------------------------------------------------------------##
def Periodic_msg_process(message):
	result = {'List of Neighbors':'','LowerBound':'','UpperBound':'','IMI':'','Latitude':'','Longitude':'','Num. Lost Msgs':''}
	## Break the message into relevant pieces.
	# message is equal to: PrdSvg:^andneigh~v2;v4;^andlwbnd~300^anduppbnd~1000^anddel~530
	#  ^andlat~49.6818137475^andlon~2.77217291505^andnbl~0
	main_pieces = message.split(":")
	## first part of main_pieces can be discarded
	## Break again to smaller pieces. Using regular expressions again
	#^andneigh~v2;v4;^andlwbnd~300^anduppbnd~1000^anddel~530^andlat~49.6818137475^andlon~2.77217291505^andnbl~0
	small_pieces = re.match(r'\^andneigh~(.*)\^andlwbnd~([0-9]*)\^anduppbnd~([0-9]*.[0-9]*)\^anddel~([0-9]*)\^andlat~([0-9]*.[0-9]*)\^andlon~([0-9]*.[0-9]*)\^andnbl~([0-9]*)',
		main_pieces[1])
	if small_pieces:
		## "== Neighbors =="
		result['List of Neighbors'] = small_pieces.group(1)
		## "== Lower Bound =="
		result['LowerBound'] = small_pieces.group(2)
		## "== Upper Bound =="
		result['UpperBound'] = small_pieces.group(3)
		## "== IMI =="
		result['IMI'] = small_pieces.group(4)
		## "== Latitude =="
		result['Latitude'] = small_pieces.group(5)
		## "== Longitude =="
		result['Longitude'] = small_pieces.group(6)
		## "== Number of lost messages =="
		result['Num. Lost Msgs'] = small_pieces.group(7)
	else:
		print ("::Periodic message didn't match::")
		print (message)
	pass
	
	return result
##---------------------------------------------------------------------------------------------##
## General Script 																			   ##
##---------------------------------------------------------------------------------------------## 
## command line parameters
script, path, filemask = argv


## creating subfolders
for alg in List_of_algorithms:
	alg_path = path + '/' + alg
	for sp in List_of_speeds:
		speed_path = alg_path + '/' + sp
		for lr in List_of_LossRates:
			lossrate_path = speed_path + '/' + lr
			print (lossrate_path)
			if os.path.exists(lossrate_path):
				print ("Verifying folder %s" %lossrate_path)
				## reading files within folders
				files = lossrate_path + '/' + filemask
				filenames = sorted(glob.glob(files))

				## Counting the number of processed files
				counter = 0

				for f in filenames:
					## opening file
					and_trace = open(f)

					## List of data frames to receive each kind of saving process: 
					#received messages; sent messages; periodic saved messages
					msgs_dict = {}
					
					for line in and_trace:
						## Comparing with the pattern
						##12/15/2015:14h07m34s:1450184854813803:PrdSvg:^andneigh~^anddel~1000^andlat~-^andlon~-
						matchObj = re.match(r'(.*):(.*):([0-9]*):(.*)',line)
					
						if matchObj:
							saving_time = matchObj.group(3)
							gen_string = matchObj.group(4)
							## saving_time registered and general message detached
							# now, process general string. Considering four cases

							## if there is an 'GPS' it's a gps message and it can be ignored
							if "GPS" in gen_string or "gps" in gen_string:
								continue
							## if there is an 'stdin' it's a received message
							elif "stdin" in gen_string:
								## processing received messages trace
								try:
									## a silly statement to check data frame existence
									exist = msgs_dict["Received_Messages"]
								except KeyError:
									## data frame doesn't exist, create it
									columns = ['TimeStamp','Sending Node(SN)','IMI','Net_Reli','Address of SN','Latitude','Longitude','Altitude',
									'Speed','Heading','Seq. Number','List of Neighbors','Payload']

									new_df = pd.DataFrame(data=np.zeros((0,len(columns))), columns=columns)
									msgs_dict["Received_Messages"] = new_df
								pass
								## Data frame created, filling
								# There will always exist a column with a TimeStamp
								insert_values = {'TimeStamp':saving_time}
								values = Received_msg_process(gen_string)
								insert_values.update(values)
								## writing into Periodic savings data frame
								msgs_dict["Received_Messages"].loc[len(msgs_dict["Received_Messages"])] = insert_values
							elif "stdout" in gen_string:
								## processing sent messages trace
								try:
									## a silly statement to check data frame existence
									exist = msgs_dict["Sent_Messages"]
								except KeyError:
									## data frame doesn't exist, create it
									columns = ['TimeStamp','Sending Node(SN)','IMI','Net_Reli','Address of SN','Latitude','Longitude','Altitude',
									'Speed','Heading','Seq. Number','List of Neighbors','Payload']
								
									new_df = pd.DataFrame(data=np.zeros((0,len(columns))), columns=columns)
									msgs_dict["Sent_Messages"] = new_df
								pass
								## Data frame created, filling
								# There will always exist a column with a TimeStamp
								insert_values = {'TimeStamp':saving_time}
								values = Sent_msg_process(gen_string)
								insert_values.update(values)
								## writing into Periodic savings data frame
								msgs_dict["Sent_Messages"].loc[len(msgs_dict["Sent_Messages"])] = insert_values
							elif "PrdSvg" in gen_string:
								## processing periodic saving trace
								try:
									## a silly statement to check data frame existence
									exist = msgs_dict["Periodic"]
								except KeyError:
									## data frame doesn't exist, create it
									columns = ['TimeStamp','List of Neighbors','LowerBound','UpperBound','IMI','Latitude',
									'Longitude','Num. Lost Msgs']
									new_df = pd.DataFrame(data=np.zeros((0,len(columns))), columns=columns)
									msgs_dict["Periodic"] = new_df
								pass
								## Data frame created, filling
								# There will always exist a column with a TimeStamp
								insert_values = {'TimeStamp':saving_time}
								values = Periodic_msg_process(gen_string)
								insert_values.update(values)
								## writing into Periodic savings data frame
								msgs_dict["Periodic"].loc[len(msgs_dict["Periodic"])] = insert_values
							else:
								print ("Message not recognized")
								print (line)
							pass
						pass
					pass
					## Writing data frames to files
					for trace in List_of_traces:
						for filename in filenames:
							#creating files in the same directory as the sources
							result_filename = filename + '.' + trace + '.csv'
							## It might happens that a node didn't received any message, or didn't sent any messages. In these cases,
							# an attempt to save files using these "traces" will generate an error. So, use "try" construction
							try:
								msgs_dict[trace].to_csv(result_filename)
							except Exception as e:
								print (e)
							pass
						pass
					pass
					counter += 1
					print ("Files processed: %d" %counter)
				pass # end of "for f in filenames:"
			pass
		pass # end of "	for lr in List_of_LossRates:"
	pass # end of "for sp in List_of_speeds:"
pass # end of "for alg in List_of_algorithms:"