#!/usr/bin/env python3

import os
import sys
import time
import shutil
import subprocess
import json

#Merger Json
def mergeJson(base, line):
	lineObj = json.loads(line.rstrip())

	for typeKey in lineObj:
		#Loop through each new type section
		lineTypeObj = lineObj[typeKey]
		if typeKey in base.keys():
			#Type exists, add elements
			for itemKey in lineTypeObj:
				#Loop through each elements in type
				obj = lineTypeObj[itemKey]
				if itemKey in base[typeKey].keys():
					#Elements exists, merging data
					if isinstance(obj,str):
						#Simple Object (New String cover old String)
						if (typeKey not in base):
							newItem = {itemKey:obj}
							base[typeKey] = newItem
						else:
							base[typeKey][itemKey] = obj
					else:
						#Complex Object (Loop and add each properties)
						for objKey in obj:
							if (typeKey not in base):
								newItem = {itemKey:{objKey:obj[objKey]}}
								base[typeKey] = newItem
							elif (itemKey not in base):
								newItem = {objKey:obj[ObjKey]}
								base[typeKey][itemKey] = newItem
							else:
								base[typeKey][itemKey][objKey] = obj[objKey]
				else:
					#Elements not exists, add full element
					if (typeKey not in base):
						newItem = {itemKey:obj}
						base[typeKey] = newItem
					else:
						base[typeKey][itemKey] = obj
		else:
		#Type not exists, add full type
			base[typeKey] = lineTypeObj
	return base

#Find if element identifier exists
def findIdentifier(base, identifier):
	for typeKey in base:
		typeObj = base[typeKey]
		#Found vertics elements group
		if identifier in typeObj:
			#If given identifier exists, it means the vertics exists
			return True
	return False

def extractElement(base, identifier):
	for typeKey in base:
		typeObj = base[typeKey]
		if identifier in typeObj:
			#Element found
			return True,typeKey,identifier,typeObj[identifier]
	return False,None,None,None

#Merge missing edges from model
def mergeEdge(base, model):
	elementKey = {'entity','agent','activity'}
	prefixKey = {'prefix'}

	for typeKey in model:
		if (typeKey not in elementKey) and (typeKey not in prefixKey):
			typeObj = model[typeKey]
			for key in typeObj:
				if not findIdentifier(base, key):
					exists,newTypeKey,newIdentifier,newObj = extractElement(model,key)
					if exists:
						if (newTypeKey not in base):
							newItem = {newIdentifier:newObj}
							base[newTypeKey] = newItem
						else:
							base[newTypeKey][newIdentifier] = newObj
	return base

#Merge missing nodes from model
def mergeNode(base, model):
	targetKey = {'prov:entity','prov:activity','prov:agent','prov:informant','prov:informed','prov:trigger','prov:generatedEntity','prov:usedEntity','prov:plan','prov:delegate','prov:responsible','prov:influencer','prov:influencee','prov:generalEntity','prov:specificEntity','prov:alternate1','prov:alternate2','prov:collection'}
	elementKey = {'entity','agent','activity'}
	prefixKey = {'prefix'}

	pending = dict()
	for typeKey in base:
		if (typeKey not in elementKey) and (typeKey not in prefixKey):
			#Loop all relation elements group
			typeObj = base[typeKey]
			for relationKey in typeObj:
				obj = typeObj[relationKey]
				for key in targetKey:
					if key in obj:						
						#Find if the vertics related by this edges is exsits
						if not findIdentifier(base, obj[key]):
							exists,newTypeKey,newIdentifier,newObj = extractElement(model,obj[key])
							if exists:
								if (newTypeKey not in base):
									if (newTypeKey not in pending):
										newItem = {newIdentifier:newObj}
										pending[newTypeKey] = newItem
									else:
										pending[newTypeKey][newIdentifier] = newObj
								else:
									base[newTypeKey][newIdentifier] = newObj
	#Add Pending Item
	for key in pending:
		if (key not in base):
			base[key] = pending[key]
		else:
			for itemKey in pending[key]:
				base[key][itemKey] = pending[key][itemKey]

	return base

#Start Camflow
def startCamflow(stagePath, workingPath, suffix, isModel):
	global camflowPath

	os.chdir(stagePath)

	#Fix config
	try:
		shutil.copyfile('/etc/camflowd.ini','/etc/camflowd.ini.backup')
		file = open('/etc/camflowd.ini','w')
		file.write('[general]\noutput=log\nlog=%s/audit.log' % workingPath)
		file.close()
	except IOError:
		pass

	#Clean camflow working history
	subprocess.call('service camflowd stop'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	if os.path.exists('/tmp/.camflowModel'):
		try:
			mtime = os.path.getmtime('/tmp/.camflowModel')
			with open('/proc/uptime', 'r') as f:
				sec = float (f.readline().split()[0])
			if (mtime < (time.time() - sec)):
				os.remove('/tmp/.camflowModel' % workingPath)
		except OSError:
			pass

	#Capture provenance
	subprocess.call('service camflowd start'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	subprocess.call(('camflow --track-file %s/test propagate' % stagePath).split())
	os.system('%s/test' % stagePath)
	subprocess.call(('camflow --track-file %s/test false' % stagePath).split())
	time.sleep(1)
	subprocess.call('service camflowd stop'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	#Process provenance result into 1 json
	file = open('%s/audit.log' % workingPath, 'r')
	next(file)
	result={}

	for line in file:
		result = mergeJson(result, line.rstrip())
	file.close()
	os.remove('%s/audit.log' % workingPath)

	if isModel:
		if os.path.exists('/tmp/.camflowModel'):
			file = open('/tmp/.camflowModel', 'r')
			line = file.read().rstrip()
			result = mergeEdge(result,json.loads(line))
			result = mergeNode(result,json.loads(line))
			file.close()
		file = open('/tmp/.camflowModel', 'w')
	else:
		if os.path.exists('/tmp/.camflowModel'):
#			file = open('/tmp/.camflowModel', 'r')
#			line = file.read().rstrip()
#			result = mergeEdge(result,json.loads(line))
#			result = mergeNode(result,json.loads(line))
#			file.close()
			#Writing result to json
			file = open('%s/output.provjson-%s' %(workingPath, suffix), 'w')
	file.write(json.dumps(result))
	file.close()

	try:
		shutil.copyfile('/etc/camflowd.ini.backup','/etc/camflowd.ini')
	except IOError:
		pass


#Retrieve arguments
trial = 0
if len(sys.argv) == 8:
	if sys.argv[7].isdigit():
		trial = int(sys.argv[7])
elif len(sys.argv) != 7:
	print ("Usage: %s <Stage Directory> <Working Directory> <Program Directory> <GCC MACRO> <CamFlow Config Directory> <suffix> [<Number of trial (Minimum / Default: 2)>]" % sys.argv[0])
	quit()

if trial < 2:
	trial = 2

stagePath = os.path.abspath(sys.argv[1])
workingPath = os.path.abspath(sys.argv[2])
progPath = os.path.abspath(sys.argv[3])
gccMacro = sys.argv[4]
camflowPath = os.path.abspath(sys.argv[5])
suffix = sys.argv[6]

#Create Model Data
subprocess.check_output(('%s/prepare %s %s --static' %(progPath, stagePath, gccMacro)).split())
startCamflow(stagePath, workingPath, '', True)

for i in range(1, trial+1):
	#Prepare the benchmark program
	subprocess.check_output(('%s/prepare %s %s --static' %(progPath, stagePath, gccMacro)).split())
	startCamflow(stagePath, workingPath, '%s-%d' % (suffix, i), False)
		
