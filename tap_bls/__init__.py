#!/usr/bin/env python3

import sys
import os
import json         # parsing json files
import datetime     # time and dates functions
import pytz         # timestamp localization / timezones
import requests     # http and api calls library  TODO: Can this be removed here?

from .update_state import generate_state, update_state
from .client import *
from .create_schemas import create_schemas
from .discover import discover

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

REQUIRED_CONFIG_KEYS = ["api-key"]


LOGGER = singer.get_logger()

# function for finding a file on the system running the tap, relative to the file running the tap.
def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


# go into the local 'schemas' folder, and pare through all the .json files you find there.
def load_schemas():
    ### Load schemas from schemas folder ###
    
    # If no schemas are found in the /schemas/ folder, then generate them using create_schemas.py
    if len([name for name in os.listdir(get_abs_path('schemas')) if os.path.isfile(os.path.join(get_abs_path('schemas'), name))]) == 0:
        create_schemas()
    
    # now grab the .json files in /schemas/ and output the catalog.json file.
    schemas = {}
    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = Schema.from_dict(json.load(file))
    return schemas   # returns a 'dict' that contains <class 'singer.schema.Schema'> objects


def sync(config, state, catalog):
    
    """ Sync data from tap source """        
    # Loop over selected streams in catalog
    # pickup_year is the most recent year value in the STATE file
    now = datetime.datetime.now()
    
    for stream in catalog.get_selected_streams(state):
        # whatisthis(state["bookmarks"].keys())
        # whatisthis(stream.schema.additionalProperties)
        # if "annual" in stream.schema.additionalProperties:
        #    print("I FOUND ANNUAL")
        
        if "startyear" in config.keys():
            stream_start_year = config['startyear']
        else:
            stream_start_year = "2000"
        
        if "endyear" in config.keys():
            stream_end_year = config['endyear']
        else:
            stream_end_year = now.year
        
        if "calculations" in config.keys():
            stream_calculations = config['calculations']
        else:
            stream_calculations = "False"
            
        if "annualaverage" in config.keys():
            stream_annualaverage = config['annualaverage']
        else:
            stream_annualaverage = "False"
            
        if "aspects" in config.keys():
            stream_aspects = config['aspects']
        else:
            stream_aspects = "False"
   
        # check if the STATE.json requests a more recent start date
        if "bookmarks" in state.keys():
            if stream.stream in state["bookmarks"].keys():
                try:
                    pickup_year = int(state["bookmarks"][stream.stream]['year'])
                except:
                    start_year = False
                    year_reset = "There was an error with the year format \""+ state[stream.stream] +"\" in the State.json file for stream " + str(stream.stream) + " - pickin up at year " + str(stream_start_year) + "."
                    LOGGER.info(year_reset)
                else:
                    start_year = int(config['startyear'])
                    if (start_year < pickup_year and pickup_year <= now.year):
                        stream_start_year = str(pickup_year)
                        year_reset = "As per state, overriding start year for stream " + str(stream.stream) + " to " + stream_start_year
                        LOGGER.info(year_reset)
                
        LOGGER.info("Syncing stream:" + stream.tap_stream_id)
        
        bookmark_column = stream.replication_key
        
        is_sorted = False  # TODO: indicate whether data is sorted ascending on bookmark value

        singer.write_schema(
            stream_name=stream.tap_stream_id,
            schema=stream.schema.to_dict(), #the "to_dict()" bit is a change to the current cookiecutter template.
            key_properties=stream.key_properties,
        )
        
        json_data = call_api({"seriesid": [stream.tap_stream_id],"startyear":stream_start_year, "endyear":stream_end_year,"calculations":stream_calculations,"annualaverage":stream_annualaverage,"aspects":stream_aspects,"registrationkey":config['api-key']})
        
        max_bookmark = 0
        max_year = 0
        utc = pytz.timezone('UTC')
        thetime = utc.localize(datetime.datetime.now())
        thetimeformatted = thetime.astimezone().isoformat()
        
        for series in json_data['Results']['series']:
            seriesId = series['seriesID']                
            time_extracted = utc.localize(datetime.datetime.now()).astimezone().isoformat()
        
            for item in series['data']:
                
                # whatisthis(item)
                
                year = item['year']
                if max_year < int(year):
                    max_year = int(year)
                period = item['period']
                if period[0] == 'M':
                    month = int(period[1]+period[2])
                    quarter = round((int(period[1]+period[2])/3)+0.3)
                elif period[0] == 'Q':
                    month = 0
                    quarter = period[2]
                elif period[0] == 'A':
                    month = 0
                    quarter = 0
                else:
                    month = ""
                    quater= ""
                value = item['value']
                full_period = str(year) + "-" + str("{0:0=2d}".format(month)) + "-01T00:00:00-04:00"
                footnotes=""
                for footnote in item['footnotes']:
                    if footnote:
                        footnotes = footnotes + footnote['text'] + ','

                next_row = {
                    "type":"RECORD",
                    "stream": seriesId,
                    "time_extracted": time_extracted,
                    "schema":seriesId,
                    "record":{
                        "SeriesID": seriesId,
                        "year": year,
                        "period": period,
                        "value": value,
                        "footnotes":footnotes[0:-1],
                        "month": str(month),
                        "quarter":str(quarter),
                        "time_extracted":time_extracted,
                        "full_period":full_period
                        }
                    }
        
                # write one or more rows to the stream:
                singer.write_records(stream.tap_stream_id,[next_row])
                # capture stream state
                if bookmark_column:
                    
                    if is_sorted:
                        # update bookmark to latest value - this is redundant for tap-bls
                        singer.write_state({stream.tap_stream_id: next_row["record"][bookmark_column[0]]})
                    else:
                        # if data unsorted, save max value until end of writes.  tap-bls goes by the year and will use this approach
                        max_bookmark = max(max_bookmark, int(next_row["record"][bookmark_column[0]]))
        if bookmark_column and not is_sorted:
            singer.write_state({stream.tap_stream_id: max_bookmark})
            if (config['update_state'].lower() == 'true') and (stream_start_year == config['startyear']):  # if you set 'uptadate_state' in config.json the *tap* will update the STATE file - note this is NOT standard behaviour in Singer data flows as the *target* should handle STATE updates.
                LOGGER.info(update_state({stream.tap_stream_id: max_bookmark}))
    return


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
            
        sync(args.config, args.state, catalog)  # run the synch


# if this file is being called as the main program, execute the function main().
if __name__ == "__main__":
    main()