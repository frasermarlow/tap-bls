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
    
    
    notes=""
    a=0
    for note in payload['message']:
        if note:
            notes = notes + note
            if a > 0:
                notes = notes + " | "
            a += 1

    if payload['status'] == "REQUEST_NOT_PROCESSED":
        LOGGER.info("The API call for series " + str(api_parameters['seriesid'][0]) + " failed. Check your API key in the config file. The API returned this error: \"" + notes + "\"")
        return False
    elif payload['status'] == "REQUEST_SUCCEEDED":
        message = "API call for series " + str(api_parameters['seriesid'][0]) + " succeeded in " + str(payload['responseTime']) + "ms"
        LOGGER.info(message)
        seriesid = payload['Results']['series'][0]['seriesID']    
        log_the_api_call_to_file("API PARAMETERS: " + str(api_parameters),seriesid)
        log_the_api_call_to_file("JSON REQUEST RESULTS: " + str(payload),seriesid)
    else:
        message = "API call for series " + seriesid + " succeeded in " + str(payload['responseTime']) + "ms but returned a status of " + payload['status']
        LOGGER.info(message)
        
    return json.loads(p.text)