""" Calls the BLS API """
#!/usr/bin/env python3

import json
import requests
import singer

LOGGER = singer.get_logger()

LOG = False  # Set to 'True' to trigger raw API call logging

def log_the_api_call_to_file(p, s):
    """ creates a log of the raw call and returned data - mostly useful for testing """
    if LOG:
        with open("api_call_"+s+".txt", "a", encoding='utf-8') as f:
            f.write(p+"\n\n")
    else:
        return

def call_api(api_parameters):
    """ gathers parameters and makes the API call. Returns FALSE if call fails """
    notes = ""
    a = 0
    headers = {'Content-type': 'application/json'}
    data = json.dumps(api_parameters)
    p = requests.post(
        'https://api.bls.gov/publicAPI/v2/timeseries/data/',
        data=data,
        headers=headers,
        timeout=120
    )
    log_the_api_call_to_file("RAW: " + str(p.text), "raw")
    payload = json.loads(p.text)

    for note in payload['message']:
        if note:
            notes = notes + note
            if a > 0:
                notes = notes + " | "
            a += 1

    if payload['status'] == "REQUEST_NOT_PROCESSED":  # API hit an error

        for idx, msg in enumerate(payload['message']):
            LOGGER.info(idx)
            if msg[0:122] == "Request could not be serviced, as the daily threshold for total number of requests allocated to the user has been reached.":
                LOGGER.info("The API call was not processed as you have hit your daily limit. The API returned this error: \"%s\"", notes)
            if msg[0:8] == "The key:":
                LOGGER.info("The API call for series %s failed. Check your API key in the config file. The API returned this error: \"%s\"", str(api_parameters['seriesid'][0]), notes)
            else:
                LOGGER.info("The API call for series %s failed. The API returned this error: \"%s\"", str(api_parameters['seriesid'][0]), notes)
            return False

    elif payload['status'] == "REQUEST_FAILED_INVALID_PARAMETERS":

        LOGGER.info("The API call for series %s failed due to invalid parameters passed along in the call. The API returned this error: \"%s\"", str(api_parameters['seriesid'][0]), notes)
        LOGGER.info("The API call was as follows: %s", str(api_parameters))
        return False

    elif payload['status'] == "REQUEST_SUCCEEDED":

        for idx, msg in enumerate(payload['message']):

            if msg[0:14] == "Invalid Series": #  API call succeeded but Series not found
                LOGGER.info("The API call succeeded but the series %s was not found. The API returned this error: \"%s\"", str(api_parameters['seriesid'][0]), notes)
                return False
            if msg[0:29] == "No Data Available for Series ":
                LOGGER.info("The API call succeeded but the series %s returned this error: \"%s\"", str(api_parameters['seriesid'][0]), msg)
                LOGGER.info("This may indicate a partial result set, so I am going to proceed.")
            else:
                message = "API call for series " \
                          + str(api_parameters['seriesid'][0]) \
                          + " succeeded in " \
                          + str(payload['responseTime']) \
                          + "ms"
                LOGGER.info(message)
                seriesid = payload['Results']['series'][0]['seriesID']
                log_the_api_call_to_file("API PARAMETERS: " + str(api_parameters), seriesid)
                log_the_api_call_to_file("JSON REQUEST RESULTS: " + str(payload), seriesid)

    else:
        log_the_api_call_to_file("ERROR: " + str(api_parameters), "error")
        log_the_api_call_to_file("JSON REQUEST RESULTS: " + str(payload), "error")
        message = "API call succeeded in " \
                  + str(payload['responseTime']) \
                  + "ms but returned a status of " + payload['status']
        LOGGER.info(message)
        return False

    if not payload['Results']['series'][0]['data']:
        message = "No data returned for series " + str(payload['Results']['series'][0]['seriesID'])
        LOGGER.info(message)
        return False

    return json.loads(p.text)
