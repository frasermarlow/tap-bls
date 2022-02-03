#!/usr/bin/python

'''

Compatible with tap-bls v 0.1.7

This file is provided as an example of pulling out BLS data from a .csv file that itself came from the BLS API.
I hope this serves as a useful template if you need to parse out the actual series datapoints.
In this case the output is formatted as javascript 'var's that get used in producing a graph using chartjs.
'''

import glob
import os
import datetime
# ----------------------------- Variables ------------------------------

bls_data_location="/home/ubuntu/bls-data/"  # folder where the singer tap places the .csv files
output_file = "/home/ubuntu/bls-data/output.txt"                  # name of the output file where the new data format will be saved

series = [
    {"series":"JTS000000000000000QUR","variable":"quitsData","comment":"QUITS: JTS000000000000000QUR [ https://api.bls.gov/publicAPI/v2/timeseries/data/JTS000000000000000QUR?latest=true ]"},
    {"series":"JTS000000000000000LDR","variable":"layoffsData","comment":"LAYOFFS: https://data.bls.gov/timeseries/JTS000000000000000LDR"},
    {"series":"LNS11300000","variable":"laborparticipationData","comment":"LABOR PARTICIPATION: https://data.bls.gov/timeseries/LNS11300000"},
    {"series":"LNS14000000","variable":"unemploymentData","comment":"UNEMPLOYMENT: https://data.bls.gov/timeseries/LNS14000000"}
]

# ----------------------------- Functions -------------------------------

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

#  Main

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
        print(latest_file)

        with open(latest_file, 'r') as f:
            for line in f:
                if line.startswith(s["series"]):
                    data.append(line[find_nth(line,",", data_column-1):find_nth(line,",", data_column)])
                    date_time_str = line[find_nth(line,",", full_period-1)+1:find_nth(line,",", full_period-1)+11]
                    date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d')
                    dates.append(date_time_obj)
                    if line[find_nth(line,",", 9)+1:find_nth(line,",", 10)]== "preliminary":
                        prelim.append(date_time_obj)

        data.reverse()
        date_min = min(dates).strftime('%b %Y')
        date_max = max(dates).strftime('%b %Y')

        if s.get("comment") is not None :
            output += "// " + s["comment"] + "\n"

        if s.get("variable") is not None :
            output += "var " + s["variable"] + " = "

        output += str(data)

        output += "; // Series from " + date_min + " to " + date_max
        if len(prelim) > 0:
            i = 0
            output += " | The data for the following dates are preliminary: "
            for d in prelim:
                output += d.strftime('%b %Y')
                if i != 0:
                    output += " | "
                i += 1
        output += "\n// end of series\n\n"

    else: # NO FILES FOUND
        print(f"I could not locate the data file for {s['series']}.")

x = open(output_file, "w")
x.writelines(output)
x.close()
print("Data saved to " + output_file)
