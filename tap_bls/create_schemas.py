#!/usr/bin/env python3
#
# Due to the nature of this tap, there are hundreds (if not thousands) if possible sources ("series") you migth want to pull from the Bureau of labor statistics databases.  The purpose of this script is to let you create all the /tap-bls/tap_bls/schema json files you need for your purpose.  Just add or remove the series from the list, then run this script.
# fraser marlow - Nov 2020

import sys
import json         # parsing json files
import os
from os import path

import singer
from singer.schema import Schema

def get_series_list():  # fetches the array of series to create from /series.json in the config folder
    series_to_create = {}
    
    series_list = sys.argv[sys.argv.index('--config')+1].rsplit('/', 1)[0]+"/series.json"
    
    if not path.exists(series_list):
        print("I could not locate file " + series_list)
    else:
        with open(series_list, "r") as jsonFile:
            series_to_create = json.load(jsonFile)

    return series_to_create

import singer
from singer import utils, metadata
LOGGER = singer.get_logger()

def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

def write_schema_to_file(series, schema_location):
    info = ""
    try:
        with open(schema_location, "w") as jsonFile:
            json.dump(series, jsonFile)
    except:
        LOGGER.info('hit an error creating the schema for ' + series['seriesID'])
    else:
        LOGGER.info('created series ' + series['seriesID'])
    return

def create_schemas():
    schemas_to_create = get_series_list()
    for series in schemas_to_create['series']:
        if str(series['create_this_schema'].lower()) == "true":
            schema_json = {
                    "type": ["null", "object"],
                    "additionalProperties":["schema", "record", "type", "stream"],
                    "seriesID" : series['seriesid'],
                    "series_description": series['description'],
                    "key_properties": ["SeriesID","full_period"],
                    "bookmark_properties": ["time_extracted"],
                    "properties":{
                        "SeriesID":{"type":["null","string"]},
                        "period":{"type":["null","string"]},
                        "value":{"type":["null","number"]},
                        "footnotes":{"type":["null","string"]},
                        "full_period":{"type":["null","string"],"format":"date-time"},
                        "time_extracted":{"type":["null","string"],"format":"date-time"}
                        }
                }
            
            schema_file = series['seriesid'] + ".json"
            schema_location = get_abs_path('schemas') + "/" + schema_file
            
            write_schema_to_file(schema_json,schema_location)