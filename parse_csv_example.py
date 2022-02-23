#!/usr/bin/python

'''
Compatible with tap-bls v 0.1.10

This file is provided as an example of pulling out BLS data from a .csv file that itself came from the BLS API.
I hope this serves as a useful template if you need to parse out the actual series datapoints.
In this case the output is formatted as javascript 'var's that get used in producing a graph using chartjs.

Updated 2/23/2022 to make use of Pandas library
'''

import glob
import os
import datetime
import pandas

verb = True # Verbose mode.

# ----------------------------- Variables ------------------------------

bls_data_location="/home/ubuntu/bls-data/"                        # folder where the singer tap places the .csv files
output_file = "/home/ubuntu/bls-data/output.txt"                  # name of the output file where the new data format will be saved

series = [
    {"series":"JTS000000000000000QUR","variable":"quitsData","comment":"QUITS: JTS000000000000000QUR [ https://api.bls.gov/publicAPI/v2/timeseries/data/JTS000000000000000QUR?latest=true ]"},
    {"series":"CIU1010000000000A", "variable": "EmplCostIndexData","comment": "Employment Cost Index (NAICS): https://data.bls.gov/timeseries/CIU1010000000000A"},
    {"series":"JTS000000000000000LDR","variable":"layoffsData","comment":"LAYOFFS: https://data.bls.gov/timeseries/JTS000000000000000LDR"},
    {"series":"LNS11300000","variable":"laborparticipationData","comment":"LABOR PARTICIPATION: https://data.bls.gov/timeseries/LNS11300000"},
    {"series":"LNS14000000","variable":"unemploymentData","comment":"UNEMPLOYMENT: https://data.bls.gov/timeseries/LNS14000000"}
]

#  ----------------------- Helper functions -----------------------------

def user_warning(*args):
    if verb:
        for t in args:
            print(t)


#  ------------------------------  Main  ---------------------------------

user_warning("---- Running the bls-transform process ----")

data_column = 4  # The data is found in the fourth column of the .csv file
full_period = 9  # The full_period timestamp is in the 9th column of the .csv file
output = ""

for s in series:
    list_of_files = glob.glob(bls_data_location+s["series"]+"-*")

    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getctime)
        data = []
        dates = []
        prelim = []
        user_warning("Pulling data from " + s["series"])

        dp = pandas.read_csv(latest_file)

        # VALUES -------------------
        dp = dp.astype({'value': 'str'})
        data = dp['value'].tolist()
        data.reverse()

        # PERIODS -------------------
        periods = dp["full_period"].tolist()
        periods_array = [datetime.datetime.strptime(date_time_str[0:10], '%Y-%m-%d') for date_time_str in periods]
        date_min = min(periods_array).strftime('%b %Y')
        date_max = max(periods_array).strftime('%b %Y')

        # PRELIMINARY FLAG -------------------

        prelims = dp.loc[dp['footnotes'].notnull()]

        if s.get("comment") is not None :
            output += "// " + s["comment"] + "\n"

        if s.get("variable") is not None :
            output += "var " + s["variable"] + " = "

        output += str(data)

        output += "; // Series from " + date_min + " to " + date_max

        if prelims.empty == False:
            i = 0
            for index, row in prelims.iterrows():
                period = datetime.datetime.strptime(row['full_period'][0:10], '%Y-%m-%d')
                output += " | " + period.strftime('%b %Y') + " marked '" + row['footnotes'] + "'"

        output += "\n// end of series\n\n"

    else: # NO FILES FOUND
        user_warning(f"Python Transform says: I could not locate the data file for {s['series']}. Please make sure the API call produced results and saved the .csv file in the right place.")

if len(output) == 0:
    user_warning("There was no data to output.")
else:
    x = open(output_file, "w"); x.writelines(output); x.close()
    user_warning("Data saved to " + output_file)
