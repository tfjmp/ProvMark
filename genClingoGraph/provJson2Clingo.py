#!/usr/bin/env python3

import os
import sys
import json
from json_merger import Merger
from json_merger.config import UnifierOps, DictMergerOps

#Generate Clingo graph string for nodes
def handleNode(type):
	global jsonObject, dict, id, label, counter, suffix
	
	if type in jsonObject:
		for nodeIdentifier in jsonObject[type]:
			node = jsonObject[type][nodeIdentifier]
			dict[nodeIdentifier] = counter
			id += "n%s(n%d,\"%s\").\n" % (suffix, counter, type)
#			label += "l%s(n%d,\"identifier\",\"%s\").\n" % (suffix, counter, nodeIdentifier)
			for labelIdentifier in node:
				label += "l%s(n%d,\"%s\",\"%s\").\n" % (suffix, counter, labelIdentifier, node[labelIdentifier])
			counter = counter+1

#Generate Clingo graph string for edges
def handleEdge(type, start, end):
	global jsonObject, dict, id, label, counter, suffix

	if type in jsonObject:
		for edgeIdentifier in jsonObject[type]:
			edge = jsonObject[type][edgeIdentifier]
			if edge[start] in dict and edge[end] in dict:
				id += "e%s(e%d, n%d, n%d, \"%s\").\n" %(suffix, counter, dict[edge[start]], dict[edge[end]], type)
#				label += "l%s(e%d,\"identifier\",\"%s\").\n" % (suffix, counter, edgeIdentifier)
				for labelIdentifier in edge:
					if labelIdentifier != start and labelIdentifier != end:
						label += "l%s(e%d,\"%s\",\"%s\").\n" % (suffix, counter, labelIdentifier, edge[labelIdentifier])
			counter = counter +1

#Check for correct numbers of arguments
if len(sys.argv) != 4:
	print ("Usage: %s <suffix> <Json Result from CamFlow> <Working Directory" % sys.argv[0])
	quit()

jsonFile = sys.argv[2]

#Switch to working directory
os.chdir(os.path.abspath(sys.argv[3]))

#Process provenance result into 1 json
file = open(jsonFile, "r")
next(file)
jsonString={}

for line in file:
	m = Merger({},jsonString,next(file).rstrip(),DictMergerOps.FALLBACK_KEEP_HEAD,UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST)
	m.merge()
	jsonString = m.merged_root

file.close()

#Intrepret Json
jsonObject = json.loads(jsonString)

id = ""
label = ""
counter = 1
dict = {}
suffix = sys.argv[1]

#Handle Nodes (activity, entity, agent)
handleNode("activity")
handleNode("entity")
handleNode("agent")

#Handle Edges (used, wasGeneratedBy, wasInformedBy, wasDerivedFrom)
counter = 1
handleEdge("used", "prov:activity", "prov:entity")
handleEdge("wasGeneratedBy", "prov:entity", "prov:activity")
handleEdge("wasInformedBy", "prov:informed", "prov:informant")
handleEdge("wasDeviredFrom", "prov:generatedEntity", "prov:usedEntity")

#Write result to output file
file = open("./clingo-%s" % suffix, "w")
file.write(id)
file.write(label)
file.close()
