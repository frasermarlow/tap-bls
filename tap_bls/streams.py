#!/usr/bin/env python3

import datetime

from singer import utils
import singer

LOGGER = singer.get_logger()

stream_object = "fake_placeholder"

STREAM_OBJECTS = {
    'stream_name': stream_object
}