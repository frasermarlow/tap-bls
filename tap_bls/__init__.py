#!/usr/bin/env python3

import sys
import os
import json         # parsing json files
import datetime     # time and dates functions
import requests     # http and api calls library  TODO: Can this be removed here?

from .update_state import generate_state, update_state
from .discover import discover, load_schemas
from .sync import do_sync

import singer
from singer import utils, metadata
from singer.catalog import Catalog, CatalogEntry

# For dumb testing - delete this function later
def whatisthis(item):
        try:
            item_name = item.__name__
        except:
            item_name = "THIS ITEM"
        print('\n',item,'\n'+ item_name +' IS TYPE: ',type(item),'\n')

REQUIRED_CONFIG_KEYS = []  # technically you do not require an API key for this to work, but you will hit limits

LOGGER = singer.get_logger()

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