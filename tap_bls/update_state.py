#!/usr/bin/env python3
#
# NOTE: This function is unusual for a Singer Tap.  The Tap should *NOT* be updating the state.json file so we recomend not using this and setting "update_state": "false" in your config.json file.
#

import sys
import json         # parsing json files
import getopt		# parse command line arguments
import os.path
from os import path

def generate_state():
	state_file = sys.argv[sys.argv.index('--config')+1].rsplit('/', 1)[0]+"/state.json"
	if not path.exists(state_file):	
		data = {"bookmarks": {}}
		with open(state_file, "w") as jsonFile:
			json.dump(data, jsonFile)
		result = True
	else:
		result = False
	return result

def update_state(state_updates):
	info = ""
	try:
		state_file = sys.argv[sys.argv.index('--state')+1]
	except:
		try:
			state_file = sys.argv[sys.argv.index('--config')+1].rsplit('/', 1)[0]+"/state.json"
		except:
			info = "No 'state.json' file was specified and could not be generated in the config folder."

	if info == "":
		with open(state_file, "r") as jsonFile:
			data = json.load(jsonFile)
		for update in state_updates:
			try:
				data['bookmarks'][update]['year'] = int(state_updates[update])
			except KeyError:
				data['bookmarks'][update] = {'year': int(state_updates[update])}
			finally:
				info = "State for stream " + update + " updated to " + str(data['bookmarks'][update]['year'])
	
	with open(state_file, "w") as jsonFile:
		json.dump(data, jsonFile)

	return info