#!/usr/bin/env python3

import sys
import os
import json         # parsing json files
import datetime     # time and dates functions
import requests     # http and api calls library  TODO: Can this be removed here?

from .update_state import generate_state, update_state
from .create_schemas import create_schemas
from .discover import discover
from .sync import do_sync

import singer
from singer import utils, metadata
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema

# For dumb testing - delete this function later
def whatisthis(item):
        try:
            item_name = item.__name__
        except:
            item_name = "THIS ITEM"
        print('\n',item,'\n'+ item_name +' IS TYPE: ',type(item),'\n')

REQUIRED_CONFIG_KEYS = []  # technically you do not require an API key for this to work, but you will hit limits

LOGGER = singer.get_logger()

# function for finding a file on the system running the tap, relative to the file running the tap.
def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


# go into the local 'schemas' folder, and pare through all the .json files you find there.
def load_schemas():
    ### Load schemas from schemas folder ###
    schemas = {}
    schemas_path = get_abs_path('schemas')
    
    # If the '/schemas/ folder is missing, create it.
    if not os.path.isdir(schemas_path):
        os.mkdir(schemas_path)

    # If no schemas are found in the /schemas/ folder, then generate them using create_schemas.py
    if len([name for name in os.listdir(schemas_path) if os.path.isfile(os.path.join(schemas_path, name))]) == 0:
        create_schemas()
    
    # now grab the .json files in /schemas/ and output the catalog.json file.

    for filename in os.listdir(schemas_path):
        path = schemas_path + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = Schema.from_dict(json.load(file))
    return schemas   # returns a 'dict' that contains <class 'singer.schema.Schema'> objects

@utils.handle_top_exception(LOGGER)  # decorates main with exception logging 
def main():
    # Parse command line arguments
    try:
        args = utils.parse_args(REQUIRED_CONFIG_KEYS)
    except FileNotFoundError:
        LOGGER.info("One of the files you specified can't be found...  check you have catalog.json, state.json and config.json at the locations you specified.")
        sys.exit(0)

    if len(args.state) == 0:    # if no state was provided
        has_state = generate_state()        # ... generate one
    else:
        has_state = True
        
    # If discover flag was passed, run discovery mode and dump output to stdout
    if args.discover:
        catalog = discover(load_schemas())
        catalog.dump()
    # Otherwise run in sync mode
    else:
        if args.catalog:
            catalog = args.catalog
        else:
            catalog = discover(load_schemas())
            LOGGER.info("You did not specify a catalog.json file, so I will create one.")
        
        if len(catalog.streams) == 0:
            LOGGER.info("The catalog.json file exists, but is empty.")
            return
        
        do_sync(args.config, args.state, catalog)  # run the synch
    return


# if this file is being called as the main program, execute the function main().
if __name__ == "__main__":
    main()