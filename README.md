# tap-bls

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap pulls raw data from the [Bureau of Labor Statistics (BLS) API](https://www.bls.gov/developers/) as follows:

1. Provides a sample list of available BLS data series that you can add to your catalog - pick from the list or add your own.
2. Runs the API to fetch the data series from the BLS and outputs the data to StdOut based on the [Singer.io](http://singer.io) format.
3. Optionally updates the tap's `STATE.json` file (which is not standard, as the `TARGET.json` typically does this, but this is an option you can set in `CONFIG.json` )

---


## PyPi package repo:

https://pypi.org/project/tap-bls/  
`pip install tap-bls`

## Extract BLS (Bureau of Labor Statistics) data using Singer.io

The BLS provides [an API for pulling data from their records](https://www.bls.gov/data/#api), and [Singer.io](https://www.singer.io/) is a common framework for building data flows.

## Installation quickguide

requirements: Python 3.5.3 & modules os, pytz, sys, json, datetime, backoff, getopt, requests, and Singer

1. Create a virtual environment, such as `python3 -m venv ~/.virtualenvs/tap-bls` and activate it with `source ~/.virtualenvs/tap-bls/bin/activate`
2. Set the local version of Python to 3.5.3: `pyenv local 3.5.3`
3. Install `wheel` with `pip install --upgrade pip wheel`
4. Install the tap in your venv using `pip install tap-bls`
5. exit the virtual environment with `deactivate`
6. make a copy of [`sample_config.json`](https://raw.githubusercontent.com/frasermarlow/tap-bls/master/sample_config.json) (as `config.json`) and [`series.json`](https://raw.githubusercontent.com/frasermarlow/tap-bls/master/series.json) (as `series.json`) from the root of the repo into your preferred configuration folder (for example I use `~/tap-bls-config`)
7. edit the `config.json` file - the main thing you want to change is the API key ("api-key": in the json file) and put in your BLS API key. You can even leave this blank if you just want to get started.
8. run the tap once in 'Discovery mode' to build your `catalog.json` file - your command will look _something_ like `~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json --discover > ~/tap-bls-config/catalog.json`
9. You can now run the tap in standard mode - if you just want to test, run it 'unpiped' with a command such as
   `~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json --catalog ~/tap-bls-config/catalog.json`
   but if you have [`tap-csv`](https://github.com/singer-io/target-csv) installed you can make pretty outputs using
   `~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json --catalog ~/tap-bls-config/catalog.json | ~/.virtualenvs/target-csv/bin/target-csv`

> note: when creating the catalog, the schemas will get created following the normal 'schema' process for Singer, adding the definition files in a 'schema' folder within the tap files ( for example in `~\.virtualenvs\tap-bls\lib\python3.6\site-packages\tap_bls\schemas`). To change the series that you want to pull, (1) make sure you have the `purge_schemas_on_discovery` parameter set to `true` in the config file, (2) edit the `series.json` file, then (3) recreate the catalog by running the discovery mode in step 7 above.

You can use a `--state` file if you like. This tap provides the option to update the State from the tap, rather than the target. If you want info on Singer `state` files [check out the docs](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md).

## So why is this tap cool?

The BLS is the most reliable source of economic data for the USA when it comes to things like unemployment rates, the cost of labor, etc. It also includes Consumer Price Indices, Inflation, Workplace injuries and a bunch of other useful stuff. [A list of topics can be found here](https://www.bls.gov/bls/topicsaz.htm) and the most popular data series (a.k.a. "The BLS Greatest Hits!") can be found [here](https://data.bls.gov/cgi-bin/surveymost?bls).

So say you wanted to know the trend for unemployment during the COVID-19 pandemic of 2020 you could simply [query the API](https://api.bls.gov/publicAPI/v2/timeseries/data/LNS14000000?startyear=2019&endyear=2021) and see that it rapidly rose from from 3.5% at the end of 2019 to a high of _14.7%_ in April 2020, and back down to 6% by March 2021.

## You need to select the BLS series you want to ingest

The volume of data available can quickly get overwhelming. Just one topic - [Producer Price Indexes - has 318 distinct data series](https://www.bls.gov/ppi/expaggseriesids.htm). Others are so complex, they provide entire excel sheets full of time series references, as is the case for the [American Time Use study](https://www.bls.gov/tus/seriesid.htm). An explanation of [how the BLS structures Series IDs for each topic can be found here](https://www.bls.gov/help/hlpforma.htm).

A good starting point when looking for available data series is [Databases, Tables & Calculators by Subject](https://www.bls.gov/data/#api) or the [data series by topic](https://www.bls.gov/cps/cpsdbtabs.htm).

With this in mind, the tap provides a framework you can use to ingest BLS data using Singer, but the catalog file would be overwhelming if we attempted to provide every available data series, even if these were maked as `unselected` in the catalog.js. So the tap comes out-of-the-box with a dozen different series taken from some of the most popular ones, but you can configure it for the data series you want to pull in by editing ./series.json.

## Grab a key

You can access BLS data without registering a key. If you do not provide an API key, you will be restricted in the volume of data you can pull. So go to the [BLS registration page](https://data.bls.gov/registrationEngine/) and grab a key. This said, even an authenticated user has limits.

## data source API (and limitations thereof)

Our data source is [version 2 of the BLS API](https://www.bls.gov/developers/) which provides a mechanism for grabbing JSON historical timeseries data, along with optional calculations and averages.

The API has some 'fair use' limitations outlined [here](https://www.bls.gov/developers/api_faqs.htm#register1) - namely 50 series per query, 500 daily queries, 50 requests per 10 seconds etc.

The BLS Public API utilizes two HTTP request-response mechanisms to retrieve data: GET and POST. GET requests data from a specified source. POST submits data to a specified resource to be processed. The BLS Public Data API uses GET to request a single piece of information and POST for all other requests.

The BLS have imposed a maximum of 20 years in the query (with the API key - and 10 years without). Bear this in mind as longer time queries will simply be cut off.

Python is the language of choice for Singer.io taps, we are going to stick with that and [sample code is provided here](https://www.bls.gov/developers/api_python.htm#python2). The BLS provide alternatives in most popular languages.

### endpoints

HTTP Type: POST
URL (JSON): https://api.bls.gov/publicAPI/v2/timeseries/data/
Header: Content-Type= application/json

### query parameters

The BLS API allows us to query multiple series in a single call, using distinct series IDs. . Registered users can include up to 50 series IDs, each separated with a comma, in the body of a request. This said, for the ease of execution we are going to call each series one at a time. Sure, this eats into our 500 daily queries, but after all this data does not chage often (monthly at most).

## config.json

This tap requires a config file although none of the parameters are _required_. This said, it will accept the following parameters. We recommend getting and adding your BLS API key to get the most out of the integration:

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
  "update_state": "false",
  "series_list_file_location": "<absolute or relative path>/series.json",
  "purge_schemas_on_discovery": true
}
```

- _user-id_ is optional. The BLS specifies it but then it's not passed in the API call ¯\\_(ツ)_/¯
- _api-key_ is your BLS issued API key
- _start year_ is the year you want your data extract to start. Not the limits: you can pull up to 20 years in one go, and most data seris start at 2000, so you do the math... If left blank it will default to 2000. [ should be a year as a string - i.e. in quote marks ]
- _endyear_ is when you want the series to end. If left blank it will default to the current year. [ should be a year as a string - i.e. in quote marks ]
- _aspects_ is an option you will find in the API documentation but setting this to 'true' has caused issues (in my experience) whereby some data points are no longer provided in the returning payload.
- _series_list_file_location_ is an optional absolute or relative path to the series.json. If not provided (and if the schemas directory is empty), the tap will look for a file named `series.json` in the same location as the `config.json` file
- _purge_schemas_on_discovery_ if set to `true`, all files in the /schema directory will be deleted when the tap is run in discovery mode.

The next three parameters are explained in more detail [on the BLS website](https://www.bls.gov/developers/api_signature_v2.htm#parameters)

| Parameter       | description                                                                                                                                                                                                | values accepted               |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| _calculations_  | provides 1,3,6 and 12 month changes in the data in both net and percentage format. If selected, these 6 additional datapoints will be included in separate columns.                                        | will accept "true" or "false" |
| _annualaverage_ | If selected, an annual data series will include a `M13` datapoint with the annual average value.                                                                                                           | will accept "true" or "false" |
| _aspects_       | Returns data series aspect data in the format `[{'name': 'Standard Error', 'value': '-', 'footnotes': [{'code': 'A', 'text': 'Dashes indicate data not available.'}]}]`. Not many BLS series include this. | will accept "true" or "false" |

- _disable_collection_ should theoretically prevent Singer from collecting additional anonymous data on your runs, which are used to help improve Singer. You can set to "true" if you like, although it appears the additional data is collected either way ¯\\_(ツ)_/¯

- _update_state_ is an uncharacteristic feature for a Singer tap. The _target_ should update `STATE` once it has established that the data has been loaded to the endpoint, but this flag allows you to instruct the `tap` to update `STATE.json` at the end of the run. So typically you would set this to 'false'.

> tap --config CONFIG [--state STATE] [--catalog CATALOG]

STATE and CATALOG are optional arguments both pointing to their own JSON file. If you do not specify a `state.json` file the tap will generate one in the same folder as the `config.json` file. tap-bls will use `STATE.json` to remember information from the previous invocation such as the point where it left off, namely the year of the most recent data point.

## Schema fields

| .                        | Monthly | Quarterly | Semi-Annual | Annual | Format                                                                                                                                        | Note                                                                            |
| ------------------------ | ------- | --------- | ----------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| annualaverage            | Y\*     | Y\*       | Y\*         | N      | float, or Null                                                                                                                                | If set in config as `"annualaverage": "true"`                                   |
| aspects                  | Y\*     | Y\*       | Y\*         | Y\*    | Array of json dicts in the format [{'name': 'Standard Error', 'value': '0.1', 'footnotes': [{}]}] - if blank, presented as empty array : `[]` | If set in config as `"aspects": "true"`                                         |
| net_change_1             | Y\*     | Y\*       | Y\*         | Y\*    | float                                                                                                                                         | If set in config as `"calculations": "true"`                                    |
| net_change_3             | Y\*     | Y\*       | Y\*         | Y\*    | float                                                                                                                                         | If set in config as `"calculations": "true"`                                    |
| net_change_6             | Y\*     | Y\*       | Y\*         | Y\*    | float                                                                                                                                         | If set in config as `"calculations": "true"`                                    |
| net_change_12            | Y\*     | Y\*       | Y\*         | Y\*    | float                                                                                                                                         | If set in config as `"calculations": "true"`                                    |
| pct_change_1             | Y\*     | Y\*       | Y\*         | Y\*    | float                                                                                                                                         | If set in config as `"calculations": "true"`                                    |
| pct_change_3             | Y\*     | Y\*       | Y\*         | Y\*    | float                                                                                                                                         | If set in config as `"calculations": "true"`                                    |
| pct_change_6             | Y\*     | Y\*       | Y\*         | Y\*    | float                                                                                                                                         | If set in config as `"calculations": "true"`                                    |
| pct_change_12            | Y\*     | Y\*       | Y\*         | Y\*    | float                                                                                                                                         | If set in config as `"calculations": "true"`                                    |
| record\_\_footnotes      | Y\*     | Y\*       | Y\*         | Y\*    | text                                                                                                                                          | Potentially returns multiple footnotes, although extremely rare.                |
| record\_\_full_period    | Y       | Y         | Y           | Y      | DateTime                                                                                                                                      | Complete date for the datapoint.                                                |
| record\_\_month          | Y       | N         | N           | N      | integer                                                                                                                                       | Month (1-12)                                                                    |
| record\_\_period         | Y       | Y         | Y           | Y      | text                                                                                                                                          | Format examples: "M11","Q2","S02","A01"                                         |
| record\_\_quarter        | N       | Y         | N           | N      | text                                                                                                                                          |
| record\_\_SeriesID       | Y       | Y         | Y           | Y      | text                                                                                                                                          | The series Id                                                                   |
| record\_\_time_extracted | Y       | Y         | Y           | Y      | DateTime                                                                                                                                      | "Complete date plus hours, minutes, seconds and a decimal fraction of a second" |
| record\_\_value          | Y       | Y         | Y           | Y      | float                                                                                                                                         |
| record\_\_year           | Y       | Y         | Y           | Y      | integer                                                                                                                                       |
| schema                   | Y       | Y         | Y           | Y      | text                                                                                                                                          | The applied schema to this series (same as series id)                           |
| stream                   | Y       | Y         | Y           | Y      | text                                                                                                                                          |
| time_extracted           | Y       | Y         | Y           | Y      | DateTime                                                                                                                                      | "Complete date plus hours, minutes, seconds and a decimal fraction of a second" |
| type                     | Y       | Y         | Y           | Y      | text                                                                                                                                          | RECORD                                                                          |
| frequency                | Y       | Y         | Y           | Y      | text                                                                                                                                          | Set to 'M','Q','S' or 'A' for monthly, quarterly or annual series.              |

- (\*) Note - the value will be included in the schema, but that does not guarantee that the API call we return a value. Sometimes the data series siply does not include data for this item.

## Autogenerating the SCHEMAs

Typically, the file `CATALOG.json` (generated during discovery) filters which streams should be synced from all the possible streams available in the /schemas/ folder.

tap-bls behaves differently because of the enormous number of potential data series you might pull from the BLS. Therefore it works as follows:

1. If no `.json` schema files are to be found in the `tap_bls/schemas/` folder, the tap will generate them for you based on the `series.json` file. The tap will look for the `series.json` file in the same folder as your `config.json` file. This allows you to rapidly select which BLS data series you want to work with. A sample 'series.json' file is found in the root of this repo with a bunch of the most popular data seris included, so you can just copy that to your main config folder.
2. Once you have a set of schema files created (manually or using the automated approach above) you can generate the Singer `catalog.json` file using the tap's --discover mode using a command such as `~/.virtualenvs/tap-bls/bin/tap-bls --config ~/tap-bls-config/config.json --discover > catalog.json` (your set up may use a different folder than 'tap-bls-config' - that is up to you.)
3. Note that to change the bls series you pull, you will modify the `series.json` to include just the series you want to pull, then rerun the tap in discovery mode to overwrite the schemas.  This will only work if you have the parameter `purge_schemas_on_discovery` set to `true` in your config.json file.

## A note on series frequency

As far as I can figure out, the BLS provides data series in the following frequencies:

- Monthly - the most common
- Bi-monthly - very uncommon ( See CUURS12BSA0 )
- Quarterly - fairly common
- Semi-Annually (6 months) - uncommon, see [CUURS12BSAF](https://data.bls.gov/timeseries/CUURS12BSAF)
- Annual - fairly common

Bi-monthly and semi-annual appear to be most prevalent in data series related to consumer price index reports.

Note that where available (and where set to 'true' in `config.json`), annual averages are should as `M13` in the dataset.

## Tap structure

There is no predefined file structure for building a Singer tap, but here is a logical structure for this particular set-up.

![tap-bls file structure](http://frasermarlow.com/img/Slide2.PNG)

## pagination

## error codes

## BLS API sourcecode

https://github.com/OliverSherouse/bls

# Open questions and to-dos

TEST SERIES:  
CES0000000001 - Monthly series without annual average  
WPUFD49104 - Monthly series with annual average  
PRS85006092 - Quarterly series with annual average  
MPU4910012 - annual series  
CUURS12BSA0 - bi-monthly series - essentially monthly, but with blank values every other month.  
https://api.bls.gov/publicAPI/v2/timeseries/data/LNS14000000?startyear=1940&endyear=1960 Series starts mid-window  
Investigate why PRS85006092 returns Q5 data which does not match annual averages.
