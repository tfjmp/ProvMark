#!/usr/bin/env python3

import os
import sys
import subprocess
from clingoFunction import *

#Check for number of argument
if len(sys.argv) != 4:
	print ("Usage: %s <Clingo Code Template File> <Graph1> <Graph2>" % sys.argv[0])
	quit()

file = open(os.path.abspath(sys.argv[1]),'r')
clingoCode = file.read()
file.close()

result = dict()

print (processGraph(sys.argv[2], sys.argv[3], clingoCode, False))