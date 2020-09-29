# tap-bls

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls raw data from [FIXME](http://example.com)
- Extracts the following resources:
  - [FIXME](http://example.com)
- Outputs the schema for each resource
- Incrementally pulls data based on the input state

---

Copyright &copy; 2018 Stitch

## Extract BLS (Bureau of Labor Statistics) data using Singer.io

The BLS provides [an API for pulling data from their records](https://www.bls.gov/data/#api), and [Singer.io](https://www.singer.io/) is a common framework for building data flows.

## Why is this cool?

Well the BLS is the most reliable source of economic data for the USA when it comes to things like unemployment rates, the cost of labor, etc. It also includes Consumer Price Indices, Inflation, Workplace injuries and a bunch  of other useful stuff. [A list of topics can be found here](https://www.bls.gov/bls/topicsaz.htm)

So say you wanted to know the monthly rate at which Americans were quitting their jobs during the 2009/2010 recession you could simply query https://api.bls.gov/publicAPI/v2/timeseries/data/JTS00000000QUR?startyear=2008&endyear=2011  and see that it rapidly dropped from 2.2% in 2007 to a low of 1.3% at the end of 2009.

## What does the tap provide

The volume of data available can quickly get overwhelming.  Just one topic - [Producer Price Indexes - has 318 distinct data series](https://www.bls.gov/ppi/expaggseriesids.htm). Others are so complex, they provide entire excel sheets full of time series references, as is the case for the [American Time Use study](https://www.bls.gov/tus/seriesid.htm). An explanation of [how the BLS structures Series IDs for each topic can be found here](https://www.bls.gov/help/hlpforma.htm).  

A good starting point when looking for available data series is [Databases, Tables & Calculators by Subject](https://www.bls.gov/data/#api)

With this in mind, the tap provides a framework you can use to ingest BLS data using Singer, but the catalog file would be overwhelming if we attempted to provide every available data series, even if these were maked as `unselected` in the catalog.js. So the tap is provided with a dozen different series taken form some of the most popular ones but may need configuration fo rthe data series you want to pull in.

## Grab a key
You can access BLS data without registering a key but it limits your data access, and keys are free.  So go to the [BLS registration page](https://data.bls.gov/registrationEngine/) and grab a key.

## config.json
This tap requires a config file with a single *required* parameter, namely your BLS API key.  

> tap --config CONFIG [--state STATE] [--catalog CATALOG]

STATE and CATALOG are optional arguments both pointing to their own JSON file.

tap-bls will use STATE remember information from the previous invocation such as the point where it left off.
The BLS offers many data sources; CATALOG is used to filter which streams should be synced.

----------------------------------------------------------------------------------------------------------

from [this article](https://www.stitchdata.com/blog/how-to-build-a-singer-tap-infographic/)
> As I begin tap development, I seek to understand the data source API, authentication, endpoints, query parameters (especially sorting and filtering), pagination, error codes, and rate limiting by reading the API documentation and by running REST GET requests with an app like Talend's API Tester. For each of the streams, I record the endpoint URL, query parameters, primary key, bookmark fields, and other metadata in streams.py. I examine the API response formats, nested objects and arrays, and field data types and create a schema.json file for each endpoint.

## data source API
Our data source API is [version 2 of the BLS API](https://www.bls.gov/developers/) which requires [registration](https://data.bls.gov/registrationEngine/). It provides a mechanism for grabbing JSON historical timeseries data. The BLS Public API utilizes two HTTP request-response mechanisms to retrieve data: GET and POST. GET requests data from a specified source. POST submits data to a specified resource to be processed. The BLS Public Data API uses GET to request a single piece of information and POST for all other requests.
Since Python is the language of choice for Singer.io taps, we are going to stick with that and ]sample code is provided here](https://www.bls.gov/developers/api_python.htm#python2).
## authentication
## endpoints
HTTP Type:	POST
URL (JSON):	https://api.bls.gov/publicAPI/v2/timeseries/data/
Header:	Content-Type= application/json

## query parameters
The BLS API allows us to query multiple series in a single call, using distinct series IDs.  . Registered users can include up to 50 series IDs, each separated with a comma, in the body of a request.
## pagination
## error codes
## API and data limits
The BLS data goes back to the year 2000, so any start date prior to 2000-01-01 will default to that date.
If you do not provide an API key, you will be restricted in the volume of data you can pull.  this said, even an authenticated user has limits:
