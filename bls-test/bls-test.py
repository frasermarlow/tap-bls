import json         # parsing json files
import datetime     # time and dates functions
import pytz         # timestamp localization / timezones
import requests     # http and api calls library
# from singer import utils, metadata


# Parse command line arguments
# args = utils.parse_args(REQUIRED_CONFIG_KEYS)
# print('\nARGUMENTS:',args,' | ',type(args),'\n')

                     #import environment variables

# data = json.dumps({"seriesid": ['JTS00000000LDR','CUUR0000SA0','SUUR0000SA0','PRS85006092'],"startyear":"2016", "endyear":"2020"})
# ['LNS11000000','LNS12000000','LNS13000000','LNS14000000','CES0000000001','CES0500000002','CES0500000007','CES0500000003','CES0500000008','PRS85006092','PRS85006112','PRS85006152','MPU4910012','CUUR0000SA0','CUUR0000AA0','CWUR0000SA0','CUUR0000SA0L1E','CWUR0000SA0L1E','WPSFD4','WPUFD4','WPUFD49104','WPUFD49116','WPUFD49207','EIUIR','EIUIQ','CIU1010000000000A','CIU2010000000000A','CIU2020000000000A']

def call_api(catalog):
	headers = {'Content-type': 'application/json'}
	data = json.dumps(catalog)
	p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
	return json.loads(p.text)

catalog = {"seriesid": ['CUUR0000AA0'],"startyear":"2020", "endyear":"2020", "registrationkey":"5fbea9aefbe24c338b9f4f92ac4516ab"}

json_data = call_api(catalog)

print(json_data)

####  End the API call

utc = pytz.timezone('UTC')
thetime = utc.localize(datetime.datetime.now())
thetimeformatted = thetime.astimezone().isoformat()

for series in json_data['Results']['series']:
    seriesId = series['seriesID']
    time_extracted = utc.localize(datetime.datetime.now()).astimezone().isoformat()

    print('{"type":"SCHEMA", "stream":"' + seriesId + '","key_properties":[],"bookmark_properties":["time_extracted"],"schema":{"type":"object", "properties":{"SeriesID":{"type":"string"},"year":{"type":"integer"},"period":{"type":"string"},"value":{"type":"number"},"footnotes":{"type":"string"},"month":{"type":"integer"},"quarter":{"type":"integer"},"time_extracted":{"type":["null","string"],"format":"date-time"}}}}')

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
        
        next_row = '{"type":"RECORD","stream":"' + seriesId + '","time_extracted":"' + time_extracted + '","schema":"' + seriesId + '","record":{"SeriesID":"'+seriesId+'","year":' + year + ',"period":"' + period + '","value":'+ value +',"footnotes":"'+ footnotes[0:-1] +'","month":'+ str(month) +',"quarter":'+ str(quarter) +',"time_extracted":"'+ time_extracted +'"}}'
        print(next_row)

closing_state = '{"type":"STATE", "value": {}}'
print(closing_state)


    # print(x) # outputs to stdOut - uncomment the next three lines to output to file.
    # output = open(seriesId + '.txt','w')
    # output.write (x.get_string())
    # output.close()