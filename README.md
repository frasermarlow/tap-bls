# tap-bls
## Extract BLS (Bureau of Labor Statistics) data using Singer.io

The BLS provides [an API for pulling data from their records](https://www.bls.gov/data/#api), and [Singer.io](https://www.singer.io/) is a common framework for building data flows.  

## Grab a key
You can access BLS data without registering a key but it limits your data access, and keys are free.  So go to the [BLS registration page](https://data.bls.gov/registrationEngine/) and grab a key.

## config.json
This tap requires a config file with a single *required* parameter, namely your BLS API key.  

> tap --config CONFIG [--state STATE] [--catalog CATALOG]

STATE and CATALOG are optional arguments both pointing to their own JSON file.

tap-bls will use STATE remember information from the previous invocation such as the point where it left off.
The BLS offers many data sources; CATALOG is used to filter which streams should be synced.
