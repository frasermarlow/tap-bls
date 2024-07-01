"""
    tap-bls core module
    Original creation date: 2020-12-7
    Updated 2024-06-30
"""
#!/usr/bin/env python3
import sys
import singer
from singer import utils, metadata
from .update_state import generate_state, update_state
from .discover import discover, load_schemas
from .sync import do_sync

REQUIRED_CONFIG_KEYS = []  # technically you do not require an API key for this to work, but you will hit limits
LOGGER = singer.get_logger()

@utils.handle_top_exception(LOGGER)  # decorates main with exception logging
def main():
    """ Main function: Checks discover mode, and calls synch() """
    # Parse command line arguments
    try:
        args = utils.parse_args(REQUIRED_CONFIG_KEYS)
    except OSError as e:
        LOGGER.info("One of the files you specified can't be found...  check you have catalog.json, state.json and config.json at the locations you specified. %s", e)
        sys.exit(0)

    if int(args.config['startyear']) > int(args.config['endyear']):
        LOGGER.info("The end year of your range precedes the start year.  Please fix the config file.")
        sys.exit(0)

    if not args.state:          # if no state was provided
        generate_state()        # ... generate one

    series_list_file_location = args.config.get('series_list_file_location', None)
    if series_list_file_location == None:
        LOGGER.info("No data series has been specified. The tap will attempt to retrieve from the default location.")
    elif series_list_file_location == "<absolute or relative path>/series.json":
        LOGGER.info("It appears you have not yet replaced the default values in the config template. Please refer to the tap documentation on how to insert your own values.")
        sys.exit(0)

    # If discover flag was passed, run discovery mode and dump output to stdout
    if args.discover:
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
