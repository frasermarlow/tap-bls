#!/usr/bin/env python3

import json
import backoff
import requests
import singer

LOGGER = singer.get_logger()

log=False  # Set to 'True' to trigger raw API call logging

def log_the_api_call_to_file(p,s):
    if not log:
        with open("api_call_"+s+".txt", "a") as f:
            f.write(p+"\n\n")
    else:
        return

def call_api(api_parameters):

    notes=""
    a=0

    headers = {'Content-type': 'application/json'}
    data = json.dumps(api_parameters)
    p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
    log_the_api_call_to_file("RAW: " + str(p.text),"raw")
    payload = json.loads(p.text)
    
    

    for note in payload['message']:
        if note:
            notes = notes + note
            if a > 0:
                notes = notes + " | "
            a += 1

    if payload['status'] == "REQUEST_NOT_PROCESSED":  # API hit an error
        LOGGER.info("The API call for series " + str(api_parameters['seriesid'][0]) + " failed. Check your API key in the config file. The API returned this error: \"" + notes + "\"")
        return False
    elif payload['status'] == "REQUEST_FAILED_INVALID_PARAMETERS":
        LOGGER.info("The API call for series " + str(api_parameters['seriesid'][0]) + " failed due to invalid parameters passed along in the call. The API returned this error: \"" + notes + "\"")
        LOGGER.info("The API call was as follows: " + str(api_parameters))
        return False
    elif payload['status'] == "REQUEST_SUCCEEDED":
        for idx, msg in enumerate(payload['message']):
            if msg[0:14] == "Invalid Series": #  API call succeeded but Series not found
                LOGGER.info("The API call succeeded but the series " + str(api_parameters['seriesid'][0]) + " was not found. The API returned this error: \"" + notes + "\"")
                return False            
            elif msg[0:29] == "No Data Available for Series ":
                LOGGER.info("The API call succeeded but the series " + str(api_parameters['seriesid'][0]) + " returned this error: \"" + msg + "\"")

        message = "API call for series " + str(api_parameters['seriesid'][0]) + " succeeded in " + str(payload['responseTime']) + "ms"
        LOGGER.info(message)
        seriesid = payload['Results']['series'][0]['seriesID']    
        # log_the_api_call_to_file("API PARAMETERS: " + str(api_parameters),seriesid)
        # log_the_api_call_to_file("JSON REQUEST RESULTS: " + str(payload),seriesid)
    else:
        # log_the_api_call_to_file("ERROR: " + str(api_parameters),"error")
        # log_the_api_call_to_file("JSON REQUEST RESULTS: " + str(payload),"error")
        message = "API call succeeded in " + str(payload['responseTime']) + "ms but returned a status of " + payload['status']
        LOGGER.info(message)
    
    if len(payload['Results']['series'][0]['data']) == 0:
        message = "No data returned for series " + str(payload['Results']['series'][0]['seriesID'])
        LOGGER.info(message)
    else:
        return json.loads(p.text)