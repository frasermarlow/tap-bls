#!/usr/bin/env python3
import os
import json
import singer
import urllib.request

import singer
from singer import utils, metadata
from singer.catalog import Catalog, CatalogEntry, write_catalog
from singer.schema import Schema
from tap_bls.discover import do_discover
from tap_bls.client import blsClient
from tap_bls.sync import do_sync

LOGGER = singer.get_logger()
@utils.handle_top_exception(LOGGER)


# What is the tap expecting to find in the config.json file ?
REQUIRED_CONFIG_KEYS = ["user-id", "api-key", "startyear", "endyear"]

# initiate the Singer logger for output messages
LOGGER = singer.get_logger()

def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

# Check the 'schemas' folder and import all the schemas from the .json files
def load_schemas():
    """ Load schemas from schemas folder """
    schemas = {}
    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = Schema.from_dict(json.load(file))
    return schemas
  
# When running in discovery mode, build what is needed for the catalog.json file
def discover():
    raw_schemas = load_schemas()
    print('\n',raw_schemas,'\n')
    streams = []  # leave this blank
    for stream_id, schema in raw_schemas.items():  # iterate through schemas and pulls the stream_id (str) and schema ('singer.schema.Schema' object) for each schema
        # TODO: populate any metadata and stream's key properties here..
        stream_metadata = []
        key_properties = []
        # next we add the object CatalogEntry (as defined in catalog.py) to our output.
        streams.append(
            CatalogEntry(
                tap_stream_id=stream_id,
                stream=stream_id,
                schema=schema,
                key_properties=key_properties,
                replication_key=None,
                replication_method=None,
                is_view=None,
                database=None,
                table=None,
                row_count=None,
                stream_alias=None,
                metadata=stream_metadata
            )
        )
    return Catalog(streams)

def sync(config, state, catalog):
    """ Sync data from tap source """
    # Loop over selected streams in catalog
    for stream in catalog.get_selected_streams(state):
        LOGGER.info("Syncing stream:" + stream.tap_stream_id)

        bookmark_column = stream.replication_key
        is_sorted = True  # TODO: indicate whether data is sorted ascending on bookmark value

        singer.write_schema(
            stream_name=stream.tap_stream_id,
            schema=stream.schema,
            key_properties=stream.key_properties,
        )

        # TODO: delete and replace this inline function with your own data retrieval process:
        tap_data = 1 # replace '1' with a function that builds the rows of data to output.

        max_bookmark = None
        for row in tap_data():
            # TODO: place type conversions or transformations here

            # write one or more rows to the stream:
            singer.write_records(stream.tap_stream_id, [row])
            if bookmark_column:
                if is_sorted:
                    # update bookmark to latest value
                    singer.write_state({stream.tap_stream_id: row[bookmark_column]})
                else:
                    # if data unsorted, save max value until end of writes
                    max_bookmark = max(max_bookmark, row[bookmark_column])
        if bookmark_column and not is_sorted:
            singer.write_state({stream.tap_stream_id: max_bookmark})
    return

@utils.handle_top_exception(LOGGER)
def main():
    # Parse command line arguments
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)

    # If discover flag was passed, run discovery mode and dump output to stdout
    if args.discover:
        catalog = discover()
        catalog.dump()
    # Otherwise run in sync mode
    else:
        if args.catalog:
            catalog = args.catalog
        else:
            catalog = discover()
        sync(args.config, args.state, catalog)

if __name__ == "__main__":
    main()