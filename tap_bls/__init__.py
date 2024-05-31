"""
    tap-bls core module
    Original creation date: 2020-12-7
    Updated 2024-05-30
"""

#!/usr/bin/env python3
from __future__ import print_function
import sys
import os
# import json         # parsing json files
# import datetime     # time and dates functions
# import requests     # http and api calls library  TODO: Can this be removed here?

import singer
from singer import utils, metadata
# from singer.catalog import Catalog, CatalogEntry

from .update_state import generate_state, update_state
from .discover import discover, load_schemas
from .sync import do_sync

REQUIRED_CONFIG_KEYS = []  # technically you do not require an API key for this to work, but you will hit limits
LOGGER = singer.get_logger()

SCHEMA_DIR = 'schemas'  # Define the relative path to the schema directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_DIR_ABSOLUTE = os.path.join(BASE_DIR, SCHEMA_DIR)

def whatisthis(item):
    """ For dumb testing - delete this function later """
    try:
        item_name = item.__name__
    except Exception as e:
        item_name = "THIS ITEM"
        print("Error '{0}' occured. Arguments {1}.".format(e.message, e.args))
    print('\n', item, '\n'+ item_name +' IS TYPE: ', type(item), '\n')


def delete_schema_files():
    """
    If the config parameter 'purge_schemas_on_discovery' is set to 'true' this function will purge out the old schema files prior to them being written back in based on the standard 'discovery' process.
    :return: None
    """
    if os.path.exists(SCHEMA_DIR_ABSOLUTE):
        LOGGER.info(SCHEMA_DIR_ABSOLUTE)
        for filename in os.listdir(SCHEMA_DIR_ABSOLUTE):
            file_path = os.path.join(SCHEMA_DIR_ABSOLUTE, filename)
            if os.path.isfile(file_path) and filename.endswith('.json'):
                os.remove(file_path)
                LOGGER.info(f"Deleted schema file: {file_path}")
    else:
        LOGGER.info(f"The old schema reference {SCHEMA_DIR_ABSOLUTE} is incorrect.")

@utils.handle_top_exception(LOGGER)  # decorates main with exception logging
def main():
    """ Main function: Checks discover mode, and calls synch() """
    # Parse command line arguments
    try:
        args = utils.parse_args(REQUIRED_CONFIG_KEYS)
    except OSError as e:
        LOGGER.info("One of the files you specified can't be found...  check you have catalog.json, state.json and config.json at the locations you specified. %s", e)
        sys.exit(0)

    if not args.state:    # if no state was provided
        generate_state()        # ... generate one

    series_list_file_location = args.config.get('series_list_file_location', None)

    # If discover flag was passed, run discovery mode and dump output to stdout
    if args.discover:
        # Read the new parameter
        delete_existing_schemas = args.config.get('purge_schemas_on_discovery', False)
        if delete_existing_schemas:
            delete_schema_files()
        catalog = discover(load_schemas(series_list_file_location))
        catalog.dump()
    # Otherwise run in sync mode
    else:
        if args.catalog:
            catalog = args.catalog
        else:
            catalog = discover(load_schemas(series_list_file_location))
            LOGGER.info("You did not specify a catalog.json file, so I will create one.")
        if not catalog.streams:
            LOGGER.info("The catalog.json file exists, but is empty.")
            return

        do_sync(args.config, args.state, catalog)  # run the synch
    return

# if this file is being called as the main program, execute the function main().
if __name__ == "__main__":
    main()
