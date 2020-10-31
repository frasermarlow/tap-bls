#!/usr/bin/env python3
#
# Due to the nature of this tap, there are hundreds (if not thousands) if possible sources ("series") you migth want to pull from the Bureau of labor statistics databases.  The purpose of this script is to let you create all the /tap-bls/tap_bls/schema json files you need for your purpose.  Just add or remove the series from the list, then run this script.
# fraser marlow - Nov 2020

schemas_to_create = [
    {
        "seriesid":"EIUIR",
        "frequency":"monthly",
        "description":"Imports - All Commodities",
        "create_this_schema":True
    },{
        "seriesid":"EIUIQ",
        "frequency":"monthly",
        "description":"Exports - All Commodities",
        "create_this_schema":True
        },
{"seriesid":"MPU4910012","frequency":"annual","description":"Private Nonfarm Business - Multifactor Productivity annual index","create_this_schema":True},
{"seriesid":"PRS85006092","frequency":"quarterly","description":"Output Per Hour - Non-farm Business Productivity","create_this_schema":True},
{"seriesid":"CES0000000001","frequency":"monthly","description":"Total Nonfarm Employment - Seasonally Adjusted","create_this_schema":True},
{"seriesid":"CES0500000002","frequency":"monthly","description":"Total Private Average Weekly Hours of All Employees - Seasonally Adjusted","create_this_schema":True},
{"seriesid":"CES0500000007","frequency":"monthly","description":"Total Private Average Weekly Hours of Prod. and Nonsup. Employees - Seasonally Adjusted","create_this_schema":True},
{"seriesid":"CES0500000003","frequency":"monthly","description":"Total Private Average Hourly Earnings of All Employees - Seasonally Adjusted","create_this_schema":True},
{"seriesid":"CES0500000008","frequency":"monthly","description":"Total Private Average Hourly Earnings of Prod. and Nonsup. Employees - Seasonally Adjusted","create_this_schema":True},
{"seriesid":"LNS11000000","frequency":"monthly","description":"Civilian Labor Force (Seasonally Adjusted)","create_this_schema":True},
{"seriesid":"LNS12000000","frequency":"monthly","description":"Civilian Employment (Seasonally Adjusted)","create_this_schema":True},
{"seriesid":"LNS13000000","frequency":"monthly","description":"Civilian Unemployment (Seasonally Adjusted)","create_this_schema":True},
{"seriesid":"LNS14000000","frequency":"monthly","description":"Unemployment Rate (Seasonally Adjusted)","create_this_schema":True},
{"seriesid":"PRS85006112","frequency":" quarterly ","description":"Nonfarm Business Unit Labor Costs","create_this_schema":True},
{"seriesid":"PRS85006152","frequency":" quarterly ","description":"Nonfarm Business Real Hourly Compensation","create_this_schema":True},
{"seriesid":"CUUR0000SA0","frequency":"monthly","description":"CPI for All Urban Consumers (CPI-U) 1982-84=100 (Unadjusted)","create_this_schema":True},
{"seriesid":"CUUR0000AA0","frequency":"monthly","description":"CPI for All Urban Consumers (CPI-U) 1967=100 (Unadjusted)","create_this_schema":True},
{"seriesid":"CWUR0000SA0","frequency":"monthly","description":"CPI for Urban Wage Earners and Clerical Workers (CPI-W) 1982-84=100 (Unadjusted)","create_this_schema":True},
{"seriesid":"CUUR0000SA0L1E","frequency":"monthly","description":"CPI-U/Less Food and Energy (Unadjusted)","create_this_schema":True},
{"seriesid":"CWUR0000SA0L1E","frequency":"monthly","description":"CPI-W/Less Food and Energy (Unadjusted)","create_this_schema":True},
{"seriesid":"WPSFD4","frequency":"monthly","description":"PPI Final Demand (Seasonally Adjusted)","create_this_schema":True},
{"seriesid":"WPUFD4","frequency":"monthly","description":"PPI Final Demand (Unadjusted)","create_this_schema":True},
{"seriesid":"WPUFD49104","frequency":"monthly","description":"PPI Final Demand less foods and energy (Unadjusted)","create_this_schema":True},
{"seriesid":"WPUFD49116","frequency":"monthly","description":"PPI Final Demand less foods energy and trade services (Unadjusted)","create_this_schema":True},
{"seriesid":"WPUFD49207","frequency":"monthly","description":"PPI Finished Goods 1982=100 (Unadjusted)","create_this_schema":True},
{"seriesid":"CIU1010000000000A","frequency":"quarterly","description":"Employment Cost Index (ECI) Civilian (Unadjusted)","create_this_schema":True},
{"seriesid":"CIU2010000000000A","frequency":"quarterly","description":"ECI Private (Unadjusted)","create_this_schema":True},
{"seriesid":"CIU2020000000000A","frequency":" quarterly ","description":"ECI Private Wage and Salaries (Unadjusted)","create_this_schema":True}
]

import sys
import json         # parsing json files
import os

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
    for series in schemas_to_create:
        if series['create_this_schema']:
            schema_json = {
                    "type": ["null", "object"],
                    "additionalProperties":["schema", "record", "type", "stream", series['frequency']],
                    "seriesID" : series['seriesid'],
                    "series_description": series['description'],
                    "key_properties": ["SeriesID","full_period"],
                    "bookmark_properties": ["time_extracted"],
                    "properties":{
                        "SeriesID":{"type":["null","string"]},
                        "year":{"type":["null","integer"]},
                        "period":{"type":["null","string"]},
                        "value":{"type":["null","number"]},
                        "footnotes":{"type":["null","string"]},
                        "month":{"type":["null","integer"]},
                        "quarter":{"type":["integer","integer"]},
                        "full_period":{"type":["null","string"],"format":"date-time"},
                        "time_extracted":{"type":["null","string"],"format":"date-time"}
                        }
                }
            
            schema_file = series['seriesid'] + ".json"
            schema_location = get_abs_path('schemas') + "/" + schema_file
            
            print(write_schema_to_file(schema_json,schema_location))