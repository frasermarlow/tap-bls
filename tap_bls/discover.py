#!/usr/bin/env python3

import os
import json

from singer import metadata
from singer.catalog import Catalog, CatalogEntry
from .streams import STREAM_OBJECTS  # stream-specific objects for handling the data model in each stream

def discover(raw_schemas):
    streams = []
    for stream_id, schema in raw_schemas.items():
        # TODO: populate any metadata and stream's key properties here..
        stream_metadata = [{"metadata":{"inclusion":"available","selected":"true"},"breadcrumb":[]}]
        key_properties = ["year"]
        rep_key = ["year"]
        rep_method = None
        streams.append(
            CatalogEntry(
                tap_stream_id=stream_id,
                stream=stream_id,
                key_properties=key_properties,
                metadata=stream_metadata,
                replication_key=rep_key,
                is_view=None,
                database=None,
                table=None,
                row_count=None,
                stream_alias=None,
                replication_method=rep_method,
                schema=schema
            )
        )
    return Catalog(streams) # object with class 'singer.catalog.Catalog'

#  everything below is from the Adroll tap

def _get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


# Load schemas from schemas folder
def _load_schemas():
    schemas = {}

    for filename in os.listdir(_get_abs_path("schemas")):
        path = _get_abs_path("schemas") + "/" + filename
        file_raw = filename.replace(".json", "")
        with open(path) as file:
            schemas[file_raw] = json.load(file)

    return schemas


def do_discover():
    raw_schemas = _load_schemas()
    catalog_entries = []

    for stream_name, schema in raw_schemas.items():
        # create and add catalog entry
        stream = STREAM_OBJECTS[stream_name]

        catalog_entry = {
            "stream": stream_name,
            "tap_stream_id": stream_name,
            "schema": schema,
            "metadata": metadata.get_standard_metadata(
                schema=schema,
                key_properties=stream.key_properties,
                valid_replication_keys=stream.replication_keys,
                replication_method=stream.replication_method,
            ),
            "key_properties": stream.key_properties
        }
        catalog_entries.append(catalog_entry)

    return Catalog.from_dict({"streams": catalog_entries})
