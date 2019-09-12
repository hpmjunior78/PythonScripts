#!/usr/bin/python3
## This python program separate traces' files from different experiment executions.
# Bertrand run many experiments with different speed and loss rate values but sent all
# files together in a unique folder. Now, I have to separate these files per experiment execution

from sys import argv
from pathlib import Path
from shutil import copyfile
import os
import glob
import sys
import re
import pandas as pd
import numpy as np


##------------------- ##
## Required data      ##
##------------------- ##
List_of_algorithms = ['and', 'etsi']
List_of_speeds = ['10kmh','30kmh','50kmh','70kmh','90kmh']
List_of_LossRates = ['lr0','lr15','lr30','lr45','lr60','lr75','lr90']
List_of_nodes = ['n1','n2','n3','n4','al1','al2','al3','al4','al5','al6','al7','al8',
				'ap1','ap2','ap3','ap4','ap5','ap6','ap7','ap8']
##---------------------------------------------------------------------------------------------##
## General Script 																			   ##
##---------------------------------------------------------------------------------------------## 

#### constructing the output folder-tree ####
# define the name of the directory to be created
output_path = "/home/moraes/Doutorado/Traces/NewExperiments"

try:  
	## creating the main folder
	if not os.path.exists(output_path):
		os.makedirs(output_path)
	pass
except OSError:
    print ("Creation of the directory %s failed" % output_path)
else:  
    print ("Successfully created the directory %s " % output_path)

try:  
	## creating subfolders
	for algo in List_of_algorithms:
		algo_path = output_path + '/' + algo
		for sp in List_of_speeds:
			speed_path = algo_path + '/' + sp
			for lr in List_of_LossRates:
				lossrate_path = speed_path + '/' + lr
				if not os.path.exists(lossrate_path):
					os.makedirs(lossrate_path)
				pass
			pass
		pass
	pass

except OSError:
    print ("Error creating %s folder." % lossrate_path)
else:  
    print ("Directory %s successfully created." % lossrate_path)

########################################################################
#### Now, take file per file and verify to which folder it belongs to ##
## command line parameters
script, path = argv

p = Path(path)

for lr in List_of_LossRates:
	subfolder = path + '/' + lr
	print ("=== Folder %s ====" % subfolder)
	if os.path.exists(subfolder):
		## Reading files in each subfolder
		files = os.listdir(subfolder)
		## For all these files I know the lossrate. I have to verify to which
		# algorithm and speed it belongs to

		## checking within each file
		for f in files:
			# Strings to control folder selection
			str_speed = ''
			str_lr = lr
			first_lb = 0 # an initial value to lowerbound
			str_algo = "etsi" # initial value to the algorithm being used
			exit = ''# String value to show whether speed and algorithm were found ou not
			
			## opening file
			file_to_open = subfolder + '/' + f
			trace = open(file_to_open)
			print ("File %s" % f)
			
			for line in trace:
				## Comparing with the pattern
				##12/15/2015:14h07m34s:1450184854813803:PrdSvg:^andneigh~^anddel~1000^andlat~-^andlon~-
				matchObj = re.match(r'(.*):(.*):([0-9]*):(.*)',line)
				if matchObj:
					gen_string = matchObj.group(4)
					## now, process general string. If there is an 'stdin' it's a received message
					
					## searching the speed ##
					# I have to check the value in strings like 'vit~30'
					# Within received messages I can find the used speed. If exit contains the character 's'
					# the speed value was found and the loop is not necessary anymore
					if "stdin" in gen_string and exit.find('s') == -1:
						# to be sure about what was the speed used in the test, it's required to check messages
						# received from the moving nodes (n1, n2, n3, n4)
						## Comparing to:
						# "stdin > AND : ANDANDAIR^andis~al7^anddel~0^andrel~1^andadr~-^lat~49.40113^lon~2.69592^alt~60.0^vit~0^hea~-^andsn~1^andneigh~^andpl~airplug-demo.gi.utc:29105 says node al7 is alive^"
						matchSendMsg = re.match(r'.*\^andis~(.*)\^anddel.*\^vit~([0-9]*.[0-9]*)\^.*', gen_string)
						if matchSendMsg:
							sender = matchSendMsg.group(1)
							## check whether it's a moving node or not
							if sender.find("n1") != -1 or sender.find("n2") != -1 or sender.find("n3") != -1 or sender.find("n4") != -1:
								speed = matchSendMsg.group(2)
								## Check what speed is being used '10kmh','30kmh','50kmh','70kmh','90kmh'
								if speed == '10':
									str_speed = '10kmh'
									exit = exit + 's' # speed found, it's not required to search anymore
								elif speed == '30':
									str_speed = '30kmh'
									exit = exit + 's' # speed found, it's not required to search anymore
								elif speed == '50':
									str_speed = '50kmh'
									exit = exit + 's' # speed found, it's not required to search anymore
								elif speed == '70':
									str_speed = '70kmh'
									exit = exit + 's' # speed found, it's not required to search anymore
								elif speed == '90':
									str_speed = '90kmh'
									exit = exit + 's' # speed found, it's not required to search anymore
								else:
									print ("Invalid speed value: %s" % speed)
								pass
								#print ("Sender: %s " % sender, " Speed: %s" % str_speed, " Exit: %s" % exit)
							pass
						pass

						
					## if there is an 'PrdSvg' it's a Periodic Saved string
					# Within these messages I can find what algorithm was used. If exit contains the character 'a'
					# the algorithm was found and the loop is not necessary anymore
					elif "PrdSvg" in gen_string and exit.find('a') == -1:
						## Break again to smaller pieces. Using regular expressions again
						#^andneigh~v2;v4;^andlwbnd~300^anduppbnd~1000^anddel~530^andlat~49.6818137475^andlon~2.77217291505^andnbl~0
						matchPrdSvg = re.match(r'.*\^andlwbnd~([0-9]*)\^.*', gen_string)
						if matchPrdSvg:
							# If the lowerbound is changing its value, it means that AND algorithm is being used.
							# If the lowerbound is not changing its value, it means that ETSI algorithm is being used.
							
							# keep the first value found
							lowerbound = matchPrdSvg.group(1)
							if first_lb == 0:
								first_lb = lowerbound
							elif first_lb != lowerbound:
								# the value has changed, AND algorithm identified
								str_algo = 'and'
								exit = exit + 'a' # algorithm found, it's not required to search anymore
							pass
							#print ("Algo: %s" % str_algo, " Exit: %s" % exit)
						pass
					pass
				pass # end of 'if matchObj'
			pass # end of 'for line in trace'

			# constructing the destination folder
			dst_folder = output_path + '/' + str_algo + '/' + str_speed + '/' + str_lr
			dst_file = dst_folder + '/' + f
			
			try:
				print ("Moving file to: %s" % dst_folder)
				#copying file to its destination folder
				copyfile(file_to_open, dst_file)
			except Exception as e:
				print ("Error copying %s " % file_to_open, " to %s " % dst_file)
				raise e
		pass # end of 'for f in files'
	pass
pass