#!/usr/bin/env python3

import os
import sys
import time
import shutil
import subprocess
import configparser

#Print help menu
def helpMenu(name):
	print ('Usage: %s <Tools> <Tools Base Directory> <Testing Program> -f <Benchmark File>' % name)
	print ('Usage: %s <Tools> <Tools Base Directory> <Testing Program> -d <Benchmark Directory>' % name)
	print ('Tools:\n\tspg:\tSPADE with Graphviz storage\n\tspn:\tSPADE with Neo4j storage\n\topu:\tOPUS\n\tcam:\tCamFlow')
	print ('Tools Base Directory: Base directory of the chosen tool (Type . to ignore)')
	print ('Benchmark File: Path to the benchmark file generated by ProvMark')
	print ('Benchmark Directory: Path to the directory containing mutliple benchmark files')

#Prepare stage and working directory
def prepareDir(directory):
	if os.path.exists(directory):
		subprocess.call(['sudo','rm','-rf',directory])
	os.makedirs(directory)
	os.chown(directory,1000,1000)

#Check Arguments
if len(sys.argv) != 6 or (sys.argv[4] != "-f" and sys.argv[4] != "-d"):
	helpMenu(sys.argv[0])
	quit()

baseDir = os.path.abspath('%s/../' % os.path.dirname(sys.argv[0]))
tool = sys.argv[1]
toolBaseDir = os.path.abspath(sys.argv[2])
testingProgram = os.path.abspath(sys.argv[3])
workingDir = os.path.abspath('%s/working/' % baseDir)
prepareDir(workingDir)
benchmarkFiles = list()
if (sys.argv[4] == "-f"):
	benchmarkFiles.append(os.path.abspath(sys.argv[5])
else:
	dir = os.path.abspath(sys.argv[5])
	temp = ['%s/%s' % (dir,name) for name in os.listdir(dir)]
	benchmarkFiles.extend(temp)
	

#Parse Config File
config = configparser.ConfigParser()
config.read('%s/config/config.ini' % baseDir)

stage1Tool = config[tool]['stage1tool']
stage2Handler = config[tool]['stage2handler']

#Stage 1 - Start the tools and generate graph for the testing program (neo4j / dot / provjson)
start = time.time()
print ('Starting stage 1...Generating provenance for the testing program from native tools')

os.system('sudo chmod +x %s/startTool/%s' % (baseDir, stage1Tool.split()[0]))
#stage1Command = 'sudo %s/startTool/%s %s %s %s %s %s %s %d' % (baseDir, stage1Tool, stageDir, workingDir, '%s' , '%s', toolBaseDir , '%s', trial)

#subprocess.call((stage1Command % (benchmarkDir, 'PROGRAM,READ=2,WRITE=2', 'program')).split()).decode().split()

print ('End of stage 1\n')
end = time.time()
t1 = end-start
