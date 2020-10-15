#!/usr/bin/env python3
import os
import json         # parsing json files
import datetime     # time and dates functions
import pytz         # timestamp localization / timezones
import requests     # http and api calls library

import singer
from singer import utils, metadata
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema

# For dumb testing - delete this function later
def whatisthis(item):
        print('\n',item,'\nTYPE: ',type(item),'\n')


REQUIRED_CONFIG_KEYS = ["calculations", "user-id", "api-key", "startyear", "endyear"]
LOGGER = singer.get_logger()


# function for finding a file on the system running the tap, relative to the file running the tap.
def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

# go into the local 'schemas' folder, and pare through all the .json files you find there.
def load_schemas():
    ### Load schemas from schemas folder ###
    schemas = {}
    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = Schema.from_dict(json.load(file))
    return schemas  # returns as object type 'dict'

def discover():
    raw_schemas = load_schemas()
    streams = []
    for stream_id, schema in raw_schemas.items():
        # TODO: populate any metadata and stream's key properties here..
        stream_metadata = [{"metadata":{"inclusion":"available","selected":"true"},"breadcrumb":[]}]
        key_properties = ["year"]
        rep_key = None
        rep_method = None
        streams.append(
            CatalogEntry(
                tap_stream_id=stream_id,
                stream=stream_id,
                key_properties=key_properties,
                metadata=stream_metadata,
                replication_key=rep_key,
                is_view=None,
                database=None,
                table=None,
                row_count=None,
                stream_alias=None,
                replication_method=rep_method,
                schema=schema    
            )
        )
    return Catalog(streams) # object with class 'singer.catalog.Catalog'

def sync(config, state, catalog):
    """ Sync data from tap source """
    
    # Loop over selected streams in catalog
    for stream in catalog.get_selected_streams(state):
        
        if stream.stream in state.keys():
            print("Pick up here and set start year to state year")
        
        LOGGER.info("Syncing stream:" + stream.tap_stream_id)
        
        bookmark_column = stream.replication_key
        is_sorted = True  # TODO: indicate whether data is sorted ascending on bookmark value


        # print('\nSTREAM ID: ',stream.tap_stream_id,'\n')
        # print('\nSCHEMA: ',stream.schema,'\n')
        # print('\nKEY PROPERTIES: ',stream.key_properties,'\n')

        singer.write_schema(
            stream_name=stream.tap_stream_id,
            schema=stream.schema.to_dict(), #the to_dict() bit is a change to the cookiecutter template.
            key_properties=stream.key_properties,
        )

        ####  SUPER MANUAL CALL STARTS HERE ####       
                
        def call_api(catalog):
            headers = {'Content-type': 'application/json'}
            data = json.dumps(catalog)
            p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
            return json.loads(p.text)
        
        fetched_series = [stream.tap_stream_id]
        
        api_variables = {"seriesid": fetched_series,"startyear":config['startyear'], "endyear":config['endyear'],"calculations":config['calculations'],"registrationkey":config['api-key']}
        
        json_data = call_api(api_variables)
        
        # print('\nLine 84: ',json_data)
        
        ####  End the API call
        max_bookmark = None        
        utc = pytz.timezone('UTC')
        thetime = utc.localize(datetime.datetime.now())
        thetimeformatted = thetime.astimezone().isoformat()
        
        for series in json_data['Results']['series']:
        
        
            seriesId = series['seriesID']                
            time_extracted = utc.localize(datetime.datetime.now()).astimezone().isoformat()
        
            for item in series['data']:
                year = item['year']
                period = item['period']
                if period[0] == 'M':
                    month = int(period[1]+period[2])
                    quarter = round((int(period[1]+period[2])/3)+0.3)
                elif period[0] == 'Q':
                    month = 0
                    quarter = period[2]
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
                        "quarter":str(quarter) ,
                        "time_extracted":time_extracted,
                        "full_period":full_period
                        }
                    }
        
                # write one or more rows to the stream:
                singer.write_records(stream.tap_stream_id,[next_row])
                
                # capture stream state
                if bookmark_column:
                    if is_sorted:
                        # update bookmark to latest value
                        singer.write_state({stream.tap_stream_id: row[bookmark_column]})
                    else:
                        # if data unsorted, save max value until end of writes
                        max_bookmark = max(max_bookmark, row[bookmark_column])
        if bookmark_column and not is_sorted:
            singer.write_state({stream.tap_stream_id: max_bookmark})               
        state_message = {'foo': 'bar'}
        singer.write_state(state_message)
    return

@utils.handle_top_exception(LOGGER)  # decorates main with exception logging 
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

# if this file is being called as the main program, execute the function main().
if __name__ == "__main__":
    main()