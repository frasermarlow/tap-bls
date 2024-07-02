""" Due to the nature of this tap, there are hundreds (if not thousands) if possible sources ('series') you might want to pull from the Bureau of Labor Statistics databases.  The purpose of this script is to let you create all the /tap-bls/tap_bls/schema json files you need for your purpose.  Just add or remove the series from the list, then run this script.
fraser marlow - Nov 2020 """

#!/usr/bin/env python3#
import sys
import json
import os
from os import path
import singer

LOGGER = singer.get_logger()


def get_series_list(series_list_file_location=None):
    """fetches the array of series to create from /series.json in the config folder

    Parameters:
    series_file_path (str): The file path to the series.json file. This can be absolute or relative to the execution directory. If not provided, will look for a file named "series.json" in the same directory as the config.json file
    """
    series_to_create = {}

    if not series_list_file_location:
        if '--config' in sys.argv:
            config_index = sys.argv.index('--config') + 1
        elif '-c' in sys.argv:
            config_index = sys.argv.index('-c') + 1
        config_path = sys.argv[config_index]
        directory = path.dirname(config_path) if '/' in config_path else '.'
        series_list_file_location = path.join(directory, "series.json")

    if not path.exists(series_list_file_location):
        print("I could not locate file " + series_list_file_location)
    else:
        with open(series_list_file_location, "r") as jsonFile:
            series_to_create = json.load(jsonFile)

    return series_to_create


def get_abs_path(thepath):
    """ fetch the absolute path of a file """
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), thepath)


def write_schema_to_file(series, schema_location):
    """ writes the schema to file """
    try:
        with open(schema_location, "w") as jsonFile:
            json.dump(series, jsonFile)
    except Exception as e:
        LOGGER.info("hit an error creating the schema for %s - %s", series["seriesID"], e)
        return False
    else:
        LOGGER.info("created schema for series %s", series["seriesID"])
    return True


def create_schemas(series_list_file_location=None):
    """
    Loops through the series.json object and creates schemas for each series specificed where the flag 'create_this_schema' is 'true'.
    If series_list_file_location is None, an attempt will be made downstream to retrieve the default lotation.
    """
    schemas_to_create = get_series_list(series_list_file_location)

    for series in schemas_to_create["series"]:
        if str(series["create_this_schema"].lower()) == "true":
            schema_json = {
                "type": ["null", "object"],
                "additionalProperties": ["schema", "record", "type", "stream"],
                "seriesID": series["seriesid"],
                "series_description": series["description"],
                "key_properties": ["SeriesID", "full_period"],
                "bookmark_properties": ["time_extracted"],
                "properties": {
                    "SeriesID": {"type": ["null", "string"]},
                    "year": {"type": ["null", "string"]},
                    "period": {"type": ["null", "string"]},
                    "value": {"type": ["null", "string"]},
                    "footnotes": {"type": ["null", "string"]},
                    "full_period": {"type": ["null", "string"], "format": "date-time"},
                    "time_extracted": {"type": ["null", "string"], "format": "date-time"},
                },
            }
            schema_file = series["seriesid"] + ".json"
            schema_location = get_abs_path("schemas") + "/" + schema_file
            write_schema_to_file(schema_json, schema_location)
