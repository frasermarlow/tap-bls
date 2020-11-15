#!/usr/bin/env python3

import json
import backoff
import requests
import singer

LOGGER = singer.get_logger()

def log_the_api_call_to_file(p,s):
    with open("api_call_"+s+".txt", "a") as f:
        f.write(p+"\n\n")

def call_api(api_parameters):
    headers = {'Content-type': 'application/json'}
    data = json.dumps(api_parameters)
    p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
    payload = json.loads(p.text)

    if payload['status'] == "REQUEST_NOT_PROCESSED":
        LOGGER.info("The API call for series " + str(api_parameters['seriesid']) + " failed. Check your API key in the config file.")
        return False
    elif payload['status'] == "REQUEST_SUCCEEDED":
        message = "API call for series " + str(api_parameters['seriesid']) + " succeeded in " + str(payload['responseTime']) + "ms"
        LOGGER.info(message)
        seriesid = payload['Results']['series'][0]['seriesID']    
        log_the_api_call_to_file("API PARAMETERS: " + str(api_parameters),seriesid)
        log_the_api_call_to_file("JSON REQUEST RESULTS: " + str(payload),seriesid)
    else:
        message = "API call for series " + seriesid + " succeeded in " + str(payload['responseTime']) + "ms but returned a status of " + payload['status']
        LOGGER.info(message)
        
    return json.loads(p.text)