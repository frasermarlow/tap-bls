#!/usr/bin/env python3

import singer
from singer import Transformer, metadata
import datetime     # time and dates functions
from .client import *   # set up API call
import pytz         # timestamp localization / timezones
from .update_state import update_state

LOGGER = singer.get_logger()

def do_sync(config, state, catalog):
    """ Sync data from tap source """        
    # Loop over selected streams in catalog
    # pickup_year is the most recent year value in the STATE file
    now = datetime.datetime.now()
    
    for stream in catalog.get_selected_streams(state):
        
        LOGGER.info("Syncing stream:" + stream.tap_stream_id)
        bookmark_column = stream.replication_key
        is_sorted = False  # TODO: indicate whether data is sorted ascending on bookmark value
        
        if "startyear" in config.keys():
            stream_start_year = config['startyear']
        else:
            stream_start_year = "2000"
        
        if ("endyear" in config.keys()) and (len(config['endyear']) > 3):
            try:
                stream_end_year = config['endyear'] if int(config['endyear']) <= now.year else now.year
            except:
                stream_end_year = now.year
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
        if "bookmarks" in state.keys():                     # check the state even has bookmarks...
            if stream.stream in state["bookmarks"].keys():  # if this stream as an entry in the state.json file...
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

        # make the call
        the_call = {"seriesid": [stream.tap_stream_id],"startyear":stream_start_year, "endyear":stream_end_year,"calculations":stream_calculations,"annualaverage":stream_annualaverage,"aspects":stream_aspects}
        
        if 'api-key' in config.keys():
            the_call["registrationkey"] = config['api-key']
            
        json_data = call_api(the_call)
        
        if not json_data:
            return
        
        raw_schema = stream.schema.to_dict()
        
        series_frequency = json_data['Results']['series'][0]['data'][0]['period'][0] # assigns 'A' for annual, 'Q' for quarterly and 'M' for monthly.
        
        if series_frequency == "A":  # series is annual
            raw_schema['properties']['year'] = {"type":["null","integer"]}
        if series_frequency == "S":  # series is semi-annual
            raw_schema['properties']['period'] = {"type":["null","integer"]}
        if series_frequency == "Q":  # series is quarterly
            raw_schema['properties']['quarter'] = {"type":["null","integer"]}
            raw_schema['properties']['year'] = {"type":["null","integer"]}
        if series_frequency == "M":  # series is monthly
            raw_schema['properties']['month'] = {"type":["null","integer"]}

        if ("calculations" in config.keys()) and (config['calculations'].lower() == "true"):
            raw_schema['properties']['net_change_1'] = {"type":["null","number"]}
            raw_schema['properties']['net_change_3'] = {"type":["null","number"]}
            raw_schema['properties']['net_change_6'] = {"type":["null","number"]}
            raw_schema['properties']['net_change_12'] = {"type":["null","number"]}
            raw_schema['properties']['pct_change_1'] = {"type":["null","number"]}
            raw_schema['properties']['pct_change_3'] = {"type":["null","number"]}
            raw_schema['properties']['pct_change_6'] = {"type":["null","number"]}
            raw_schema['properties']['pct_change_12'] = {"type":["null","number"]}
        
        if ("aspects" in config.keys()) and (config['aspects'].lower() == "true"):
            raw_schema['properties']['aspects'] = {"type":["null","string"]}
            
        if ("annualaverage" in config.keys()) and (config['annualaverage'].lower() == "true"):
            raw_schema['properties']['annualaverage'] = {"type":["null","number"]}
        
        singer.write_schema(
            stream_name=stream.tap_stream_id,
            schema=raw_schema, #the "to_dict()" bit is a change to the current cookiecutter template on Github.
            key_properties=stream.key_properties,
        )
        
        max_bookmark = 0
        max_year = 0
        utc = pytz.timezone('UTC')
        thetime = utc.localize(datetime.datetime.now())
        thetimeformatted = thetime.astimezone().isoformat()
        
        for series in json_data['Results']['series']:
            seriesId = series['seriesID']                
            time_extracted = utc.localize(datetime.datetime.now()).astimezone().isoformat()
        
            for item in series['data']:                
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
                elif period[0] == 'S':
                    month = 0
                    quarter = 0
                    period = period[2]
                elif period[0] == 'A':
                    month = 0
                    quarter = 0
                else:
                    month = ""
                    quater= ""
                value = item['value']
                
                
                # if series_frequency == "A":
                #    next_row['year'] = item['something']
                # if series_frequency == "Q":
                #    next_row['quarter'] = item['something']
                #    next_row['year'] = item['something']
                # if series_frequency == "M":
                #    next_row['month'] = item['something']
                
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
                    "frequency":series_frequency,
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
              
                
                if ("calculations" in config.keys()) and (config['calculations'].lower() == "true"):
                    if ("calculations" in item.keys()):
                        if ("net_changes" in item["calculations"].keys()):
                            next_row['net_change_1'] = float(item['calculations']['net_changes']['1']) if '1' in item['calculations']['net_changes'].keys() else None
                            next_row['net_change_3'] = float(item['calculations']['net_changes']['3'])  if '3' in item['calculations']['net_changes'].keys() else None
                            next_row['net_change_6'] = float(item['calculations']['net_changes']['6'])  if '6' in item['calculations']['net_changes'].keys() else None
                            next_row['net_change_12'] = float(item['calculations']['net_changes']['12'])  if '12' in item['calculations']['net_changes'].keys() else None
                        else:
                            next_row['net_change_1'] = next_row['net_change_3'] = next_row['net_change_6'] = next_row['net_change_12'] = None
                        
                        if ("net_changes" in item["calculations"].keys()):
                            next_row['pct_change_1'] = float(item['calculations']['pct_changes']['1']) if '1' in item['calculations']['pct_changes'].keys() else None
                            next_row['pct_change_3'] = float(item['calculations']['pct_changes']['3']) if '3' in item['calculations']['pct_changes'].keys() else None
                            next_row['pct_change_6'] = float(item['calculations']['pct_changes']['6']) if '6' in item['calculations']['pct_changes'].keys() else None
                            next_row['pct_change_12'] = float(item['calculations']['pct_changes']['12']) if '12' in item['calculations']['pct_changes'].keys() else None
                        else:
                            next_row['pct_change_1'] = next_row['pct_change_3'] = next_row['pct_change_6'] = next_row['pct_change_12'] = None
                    else:
                        next_row['net_change_1'] = next_row['net_change_3'] = next_row['net_change_6'] = next_row['net_change_12'] = next_row['pct_change_1'] = next_row['pct_change_3'] = next_row['pct_change_6'] = next_row['pct_change_12'] = None
                
                if ("aspects" in config.keys()) and (config['aspects'].lower() == "true"):
                    next_row['aspects'] = str(item['aspects'])
                    
                if ("annualaverage" in config.keys()) and (config['annualaverage'].lower() == "true"):
                    if period == 'M13' or period == 'Q5' :
                        next_row['annualaverage'] = float(item['value'])
                    else:
                        next_row['annualaverage'] = None
        
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