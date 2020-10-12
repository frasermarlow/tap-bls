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

REQUIRED_CONFIG_KEYS = ["user-id", "api-key", "startyear", "endyear"]
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
        key_properties = []
        streams.append(
            CatalogEntry(
                tap_stream_id=stream_id,
                stream=stream_id,
                schema=schema,
                key_properties=key_properties,
                metadata=stream_metadata,
                replication_key=None,
                is_view=None,
                database=None,
                table=None,
                row_count=None,
                stream_alias=None,
                replication_method=None,
            )
        )
    return Catalog(streams) # object with class 'singer.catalog.Catalog'


def sync(config, state, catalog):
    """ Sync data from tap source """
    # Loop over selected streams in catalog
    for stream in catalog.get_selected_streams(state):
        LOGGER.info("Syncing stream:" + stream.tap_stream_id)
        
        # print('\n',stream,' | ',type(stream),'\n')
        # print('this stream id',stream.tap_stream_id,'\n')
        
        bookmark_column = stream.replication_key
        is_sorted = True  # TODO: indicate whether data is sorted ascending on bookmark value

        # singer.write_schema(
        #     stream_name=stream.tap_stream_id,
        #     schema=stream.schema,
        #     key_properties=stream.key_properties,
        # )

        ####  SUPER MANUAL CALL STARTS HERE ####       
                
        def call_api(catalog):
            headers = {'Content-type': 'application/json'}
            data = json.dumps(catalog)
            p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
            return json.loads(p.text)
        
        fetched_series = [stream.tap_stream_id]
        
        catalog = {"seriesid": fetched_series,"startyear":"2019", "endyear":"2020", "registrationkey":"5fbea9aefbe24c338b9f4f92ac4516ab"}
        
        json_data = call_api(catalog)
        
        # print('\nLine 84: ',json_data)
        
        ####  End the API call
        max_bookmark = None        
        utc = pytz.timezone('UTC')
        thetime = utc.localize(datetime.datetime.now())
        thetimeformatted = thetime.astimezone().isoformat()
        
        for series in json_data['Results']['series']:
            seriesId = series['seriesID']
            time_extracted = utc.localize(datetime.datetime.now()).astimezone().isoformat()
        
            # print('{"type":"SCHEMA", "stream":"' + seriesId + '","key_properties":[],"bookmark_properties":["time_extracted"],"schema":{"type":"object", "properties":{"SeriesID":{"type":"string"},"year":{"type":"integer"},"period":{"type":"string"},"value":{"type":"number"},"footnotes":{"type":"string"},"month":{"type":"integer"},"quarter":{"type":"integer"},"time_extracted":{"type":["null","string"],"format":"date-time"}}}}')
        
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
                footnotes=""
                for footnote in item['footnotes']:
                    if footnote:
                        footnotes = footnotes + footnote['text'] + ','
                
                next_row = {"type":"RECORD","stream": seriesId,"time_extracted": time_extracted,"schema":seriesId,"record":{"SeriesID": seriesId,"year": year,"period": period,"value": value,"footnotes":footnotes[0:-1],"month": str(month),"quarter":str(quarter) ,"time_extracted":time_extracted}}
        
                # write one or more rows to the stream:
                singer.write_records(stream.tap_stream_id,[next_row])
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

