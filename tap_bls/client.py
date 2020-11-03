#!/usr/bin/env python3

import json
import backoff
import requests

def log_the_api_call_to_file(p):
    with open("api_call.txt", "a") as f:
        f.write(p+"\n\n")

def call_api(api_parameters):
    headers = {'Content-type': 'application/json'}
    data = json.dumps(api_parameters)
    p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
    
    log_the_api_call_to_file("API PARAMETERS: " + str(api_parameters))
    log_the_api_call_to_file("JSON REQUEST RESULTS: " + str(json.loads(p.text)))
    
    return json.loads(p.text)