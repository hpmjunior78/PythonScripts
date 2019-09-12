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
output_path = "/home/moraes/Doutorado/Traces/NewExperiments/emu"

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
	for alg in List_of_algorithms:
		alg_path = output_path + '/' + alg
		for sp in List_of_speeds:
			speed_path = alg_path + '/' + sp
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
	if os.path.exists(subfolder):
		## Reading files in each subfolder
		files = os.listdir(subfolder)
		## For all these files I know the lossrate. I have to verify to which
		# algorithm and speed it belongs to

		## checking within each file
		for f in files:
			
			## auxiliar variables
			lowest_time = 0
			highest_time = 0
			exit = 0

			## opening file
			file_to_open = subfolder + '/' + f
			trace = open(file_to_open)
			print ("***** EMU file %s" % file_to_open)
			
			for line in trace:
				## Comparing with the pattern
				###06/11/2018:11h02m44s:1528707764356919:1528707764356:n1;al1 al2 al3 al4 al5 al6 al7 ap1 ap2 ap3 ap4
				###ap5 ap6 ap7 ap8:n2;al1 al2 al3 al4 al5 al6 al7 al8 ap1 ap2 ap3 ap4 ap5 ap6 ap7 ap8 n3 n4
				matchObj = re.match(r'(.*):(.*):([0-9]*):([0-9]*):(.*)',line)
				
				if matchObj:
					saving_time = matchObj.group(3)
		
					## check for the lowest saving time
					if lowest_time == 0 or float(saving_time) < lowest_time:
						lowest_time = float(saving_time)
					pass

					## check for the highest saving time
					if float(saving_time) > highest_time:
						highest_time = float(saving_time)
					pass
				pass
			pass
			#print ("EMU: lowest_time: %s " %lowest_time, "highest_time: %s" %highest_time)

			## With the lowest and highest timestamps of EMU, search these values in AND/ETSI traces
			# It should match with only one file
			initial_path = "/home/moraes/Doutorado/Traces/NewExperiments"
			for algo in List_of_algorithms:
				algo_path = initial_path + '/' + algo
				for speed in List_of_speeds:
					speed_path = algo_path + '/' + speed
					## I know the loss rate from the EMU folder.. using it
					lr_path = speed_path + '/' + lr
					if os.path.exists(lr_path):
						## Reading files in each subfolder
						#algo_files = os.listdir(lr_path)
						
						## interested node
						int_node = 'n1'
						# selecting trace for node n1 only
						algo_f = glob.glob(lr_path + '/' + "*n1*")
						#print ("algo_files: %s" %algo_files)
						#print ("File found: %s" %algo_f)
						#sys.exit()

							
						## checking within each file
						#for algo_f in algo_files:
						
						## auxiliary variables
						algo_lowest_time = 0
						algo_highest_time = 0

						line_counter = 0
						match_counter = 0

						## opening file
						#algo_file = lr_path + '/' + algo_f
						#algo_trace = open(algo_file)
						
						algo_trace = open(algo_f[0])
						#print ("Algo_File %s" % algo_file)
			
						for algo_line in algo_trace:
							## Comparing with the pattern
							##12/15/2015:14h07m34s:1450184854813803:PrdSvg:^andneigh~^anddel~1000^andlat~-^andlon~-
							matchLine = re.match(r'(.*):(.*):([0-9]*):(.*)',algo_line)
							if matchLine:
								algo_saving_time = matchLine.group(3)
								line_counter += 1

								## Here I'm doing a counter to check how many lines (saving times) match with
								# EMU saving times. By matching with EMU I mean being between the lowest and the
								# highest time of EMU trace. Finally, I make a calculus of the percentage of matching lines
								if lowest_time <= float(algo_saving_time) and highest_time >= float(algo_saving_time):
									match_counter += 1
									pass
							pass
						pass

						#print ("Algo: lowest_time: %s " %algo_lowest_time, "highest_time: %s" %algo_highest_time)
						# If the matching percentage is bigger than 90%, then the relation was found
						matching_percentage = float(match_counter) / line_counter
						if matching_percentage >= 0.9:
							## then the emu time contains this algo_file time
							#print ("The EMU file %s" %f, " contains the time of file %s" %algo_f[0])
							
							# constructing the destination folder
							dst_folder = output_path + '/' + algo + '/' + speed + '/' + lr
							dst_file = dst_folder + '/' + f
							#print ("Move file to: %s" % dst_folder)

							try:
								#copying file to its destination folder
								copyfile(file_to_open, dst_file)
								print ("copying file %s" %file_to_open, " to %s" %dst_file)
								exit = 1
							except Exception as e:
								print ("Error copying %s " % file_to_open, " to %s " % dst_file)
								raise e
						pass
						#if exit == 1:
						#	break ## finish the search in algo files
						#pass
						#pass
					pass
					if exit == 1:
						break ## finish the search in speed folders
					pass
				pass
				if exit == 1:
					break ## finish the search in algo folders
				pass
			pass
		pass # end of 'for f in files'
	pass
pass