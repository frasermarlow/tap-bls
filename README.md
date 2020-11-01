# tap-bls

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap pulls raw data from the [Bureau of Labor Statistics (BLS) API](https://www.bls.gov/developers/) as follows:
1) Provides a list of available BLS data series that you can add to your catalog - pick from the list or add your own.
2) Runs the API to fetch the data series from the BLS and outputs the data to StdOut based on the [Singer.io](http://singer.io) format.
3) Optionally updates the tap's `STATE.json` file (which is not standard, as the `TARGET.json` typically does this, but this is an option you can set in `CONFIG.json` )

---

Copyright &copy; 2020 Stitch

## Installation quickguide
1) Create a virtual environment
2) Install the tap in your venv using `pip install tap-bls`  # THIS WILL BE TRUE ONCE THIS IS PACKAGED UP! FOR NOW JUST CLONE THE REPO
3) make a copy of `config.json` and `series.json` into your preferred configuration folder (for example I use `~/tap-bls-config`) 
4) edit the `config.json` file - the main thing you want to change is the API key ("api-key": in the json file) and put in your BLS API key.  You can even leave this blank if you just want to get started.
5) run the tap once in 'Discovery mode' to build your `catalog.json` file - your command will look *something* like ```~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json --discover > ~/tap-bls-config/catalog.json```
6) You can now run the tap in standard mode - if you just want to test, run it 'unpiped' with a command such as ```~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json --catalog ~/tap-bls-config/catalog.json | ~/.virtualenvs/target-csv/bin/target-csv``` but if you have `tap-csv` file installed you can make pretty outputs using ```~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json --catalog ~/tap-bls-config/catalog.json | ~/.virtualenvs/target-csv/bin/target-csv``` 

You can use a `--state` file if you like.

## Extract BLS (Bureau of Labor Statistics) data using Singer.io

The BLS provides [an API for pulling data from their records](https://www.bls.gov/data/#api), and [Singer.io](https://www.singer.io/) is a common framework for building data flows.

## Why is this cool?

The BLS is the most reliable source of economic data for the USA when it comes to things like unemployment rates, the cost of labor, etc. It also includes Consumer Price Indices, Inflation, Workplace injuries and a bunch  of other useful stuff. [A list of topics can be found here](https://www.bls.gov/bls/topicsaz.htm) and the most popular data series (a.k.a. "The BLS Greatest Hits!") can be found [here](https://data.bls.gov/cgi-bin/surveymost?bls).

So say you wanted to know the monthly rate at which Americans were quitting their jobs during the 2009/2010 recession you could simply query https://api.bls.gov/publicAPI/v2/timeseries/data/JTS00000000QUR?startyear=2008&endyear=2011  and see that it rapidly dropped from 2.2% in 2007 to a low of 1.3% at the end of 2009.

## What does the tap provide

The volume of data available can quickly get overwhelming.  Just one topic - [Producer Price Indexes - has 318 distinct data series](https://www.bls.gov/ppi/expaggseriesids.htm). Others are so complex, they provide entire excel sheets full of time series references, as is the case for the [American Time Use study](https://www.bls.gov/tus/seriesid.htm). An explanation of [how the BLS structures Series IDs for each topic can be found here](https://www.bls.gov/help/hlpforma.htm).  

A good starting point when looking for available data series is [Databases, Tables & Calculators by Subject](https://www.bls.gov/data/#api) or the [data series by topic](https://www.bls.gov/cps/cpsdbtabs.htm).

With this in mind, the tap provides a framework you can use to ingest BLS data using Singer, but the catalog file would be overwhelming if we attempted to provide every available data series, even if these were maked as `unselected` in the catalog.js. So the tap is provided with a dozen different series taken form some of the most popular ones but may need configuration fo rthe data series you want to pull in.

## Grab a key
You can access BLS data without registering a key but it limits your data access, and keys are free.  So go to the [BLS registration page](https://data.bls.gov/registrationEngine/) and grab a key.


## data source API (and limitations thereof)
Our data source is [version 2 of the BLS API](https://www.bls.gov/developers/) which provides a mechanism for grabbing JSON historical timeseries data. 

The API allows for a free [registration](https://data.bls.gov/registrationEngine/). If you do not provide an API key, you will be restricted in the volume of data you can pull.  This said, even an authenticated user has limits.

The BLS Public API utilizes two HTTP request-response mechanisms to retrieve data: GET and POST. GET requests data from a specified source. POST submits data to a specified resource to be processed. The BLS Public Data API uses GET to request a single piece of information and POST for all other requests.
The API has some 'fair use' limitations outlined [here](https://www.bls.gov/developers/api_faqs.htm#register1) - namely 50 series per query, 500 daily queries, 50 requests per 10 seconds etc.

The BLS data goes back to the year 2000, so any start date prior to 2000-01-01 will default to that date.
Also the BLS have imposed a maximum of 20 years in the query.  Since most data series go back to 2000, the year 2020 seemed like an optimum time to develop a tap with a 20 year historical limit!

Python is the language of choice for Singer.io taps, we are going to stick with that and [sample code is provided here](https://www.bls.gov/developers/api_python.htm#python2).  The BLS provide alternatives in most popular languages.

### authentication
Authentication is through an API key which is free to get but requires [registration](https://data.bls.gov/registrationEngine/).

### endpoints
HTTP Type:	POST
URL (JSON):	https://api.bls.gov/publicAPI/v2/timeseries/data/
Header:	Content-Type= application/json

### query parameters
The BLS API allows us to query multiple series in a single call, using distinct series IDs.  . Registered users can include up to 50 series IDs, each separated with a comma, in the body of a request. This said, for the ease of execution we are going to call each series one at a time.  Sure, this eats into our 500 daily queries, but after all this data does not chage often (monthly at most).

## config.json
This tap requires a config file with a single *required* parameter, namely your BLS API key.  This said, it will accept the following parameters:

```
{
  "user-id": "your.name@emailprovider.com",
  "api-key": "your-bls-issued-api-key-goes-here",
  "startyear": "2019",
  "endyear": "2020",
  "calculations": "true",
  "annualaverage": "false",
  "aspects": "false",
  "disable_collection": "true",
  "update_state": "false"
}
```

- *user-id* is optional.  the BLS specifies it but then it's not passed in the API call ¯\\_(ツ)_/¯
- *api-key* is your BLS issues API key
- *start year* is the year you want your data extract to start.  Not the limits: you can pull up to 20 years in one go, and most data seris start at 2000, so you do the math...  If left blank it will default to 2000. [ should be a year as a string - i.e. in quote marks ]
- *endyear* is when you want the series to end.  If left blank it will default to the current year.  [ should be a year as a string - i.e. in quote marks ]

The next three parameters are explained in more detail [on the BLS website](https://www.bls.gov/developers/api_signature_v2.htm#parameters)
**THESE PARAMETERS HAVE NOT BEEN IMPLEMENTED AS OF YET AND WILL BE IGNORED!**
Parameter |  description |  values accepted
----------|--------------|-----------------
*calculations*  | provides 1,3,6 and 12 month changes in the data in both net and percentage format |   will accept "true" or "false"
*annualaverage* | brings in additional data the BLS provides |   will accept "true" or "false"
*aspects*       | brings in additional data the BLS provides |   will accept "true" or "false"


- *disable_collection* should theoretically prevent Singer from collecting additional anonymous data on your runs, which are used to help improve singer.  You can set to "true" if you like, although it appears the additional data is collected either way ¯\\_(ツ)_/¯


- *update_state* is an uncharacteristic feature for a Singer tap.  The *target* should update `STATE` once it know the data has been loaded to the endpoint, but for some side project this tap was designed for, this flag allows you to instruct the `tap` to update `STATE.json` at the end of the run.  So typically you would set this to 'false'.

> tap --config CONFIG [--state STATE] [--catalog CATALOG]

STATE and CATALOG are optional arguments both pointing to their own JSON file.  If you do not specify a `state.json` file the tap will generate one in the same folder at the `config.json` file. tap-bls will use `STATE.json` to remember information from the previous invocation such as the point where it left off, namely the year of the most recent data point.

## Autogenerating the SCHEMAs
Typically, the file `CATALOG.json` (generated during discovery) is used to filter which streams should be synced from all the possible streams available in the /schemas/ folder.  

tap-bls behaves a bit differently because of the enormous number of potential data series you migth pull from the BLS.  Therefore it works as follows:
1) If no `.json` schema files are to be found in the `tap_bls/schemas/` folder, the tap will generate them for you based on the `series.json` file.  The tap will look for the `series.json` file in the same folder as your `config.json` file.  This allows you to rapidly select which BLS data series you want to work with.
2) Once you have a set of schema files created (manually or using the automated approach above) you can generate the Singer `catalog.json` file using the tap's --discover mode using a command such as ```~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json --discover > catalog.json``` (your set up may use a different folder than 'tap-bls-config' - that is up to you.)





## pagination

## error codes

