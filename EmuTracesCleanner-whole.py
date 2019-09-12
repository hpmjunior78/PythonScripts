#!/usr/bin/python3
## This python program "cleans" EMU saved traces eliminating lines like:
## 04/17/2018:15h25m31s:1523971531510401:<I/O> : "stdin > EMU : ANDEMULCH^emuhst~v3^emurcv~true^"
## and keeping only files like:
## 04/17/2018:15h25m32s:1523971532518883:1523971532518:v1;v2 v3 v4:v2;v1 v3 v4:v3;v1 v2 v4:v4;v1 v2 v3
## I'm using the "<I/O>" string to identify and eliminate these lines
from sys import argv
from pathlib import Path
import glob
import sys
import pandas as pd
import numpy as np

##---------------------------------------------------------------------------------------------##
## General Script 																			   ##
##---------------------------------------------------------------------------------------------## 
## command line parameters
script, path, filemask = argv

p = Path(path)
print ("===== subfolders =====")
print (list(p.glob('*')))
subfolders = list(p.glob('*'))
for subfolder in subfolders:
	print (subfolder)
	#sys.exit()	
	files = subfolder / filemask
	print (files)
	filenames = sorted(glob.glob(files))
	print ("===== FILES =====")
	print (filenames)
	pass


sys.exit()
files = path + filemask
filenames = sorted(glob.glob(files))

for f in filenames:
	## opening input file
	and_trace = open(f)

	## opening output file
	output_filename = f + '.clean'
	output_file = open(output_filename,"w") 

	for line in and_trace:
		##If there is <I/O> or Timestamp strings in the line, ignore the entire line
		if "Timestamp" in line:
			## bad line identified. Drop it
			print ("bad")
		elif "<I/O>" in line:
			## bad line identified. Drop it
			print ("bad")
		else:
			## good line identified. keep it
			print (line)
			## write a new file with the clean trace
			output_file.write(line)
		pass
	pass
	output_file.close()
pass