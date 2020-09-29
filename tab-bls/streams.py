# streams: API URL endpoints to be called
# properties:
#   <root node>: Plural stream name for the endpoint
#   path: API endpoint relative path, when added to the base URL, creates the full path,
#       default = stream_name
#   key_properties: Primary key fields for identifying an endpoint record.
#   replication_method: INCREMENTAL or FULL_TABLE
#   replication_keys: bookmark_field(s), typically a date-time, used for filtering the results
#        and setting the state
#   params: Query, sort, and other endpoint specific parameters; default = {}
#   data_key: JSON element containing the results list for the endpoint; default = 'results'
#   bookmark_query_field: From date-time field used for filtering the query
#   alt_character_set: Alternate character set to try if UTF-8 decoding does not work

STREAMS = {
    # Reference: https://github.com/COVID19Tracking/covid-tracking-data/blob/master/data/us_daily.csv
    # 
    'c19_trk_us_daily': {
    api_url: 'https://api.bls.gov/publicAPI/v2/timeseries/data/',
    series_id: 'JTS00000000LDR',
    api_method: 'get',
    startyear: '2000',
    endyear: '2020'    
    }
    # Add new streams here
}
