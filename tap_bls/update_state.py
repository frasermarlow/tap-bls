""" Update the STATE.json file after each stream is synch'ed """
#!/usr/bin/env python3
#
# NOTE: This function is unusual for a Singer Tap.  The Tap should *NOT* be updating the state.json file so we recomend not using this and setting "update_state": "false" in your config.json file.
#
from __future__ import print_function
import sys
import json # parsing json files
# import getopt # parse command line arguments
from os import path


def generate_state():
    """ If the STATE.json file is missing, create one """
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
    """ update the state file - although note target should do this """
    info = ""
    try:
        state_file = sys.argv[sys.argv.index('--state')+1]
    except Exception as e1:
        try:
            state_file = sys.argv[sys.argv.index('--config')+1].rsplit('/', 1)[0]+"/state.json"
        except Exception as e2:
            info = "No 'state.json' file was specified and could not be generated in the config folder. " + e1 + " | " + e2

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
