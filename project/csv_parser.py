#!/usr/bin/env python3

import sys
import os.path


CSV_FILE = os.path.join(os.path.dirname(__file__), 'sunspots.csv')


def read_data():
    """Read in the CSV file and return a list of dictionaries."""
    data = []

    # Parsing this by splitting a string and putting the data in
    # dictionaries instead of using the built-in CSV library in
    # Python.
    with open(CSV_FILE, 'r') as f:
        raw_data = (line.split(',') for line in f)

        # Add each item from the raw split data with an incrementing
        # id number and with strings converted to numbers.
        for i, row in enumerate(raw_data):
            data.append({
                'id': i, 'year': int(row[0]), 'spots': int(row[1])
            })

    return data


def read_data_range(start=None, end=None):
    """Return data from a start to end point, inclusive.

    This uses a relatively naive approach of just going through the
    rows of data linearly.
    """

    data = read_data()

    # By default we use the whole range, the end index is not
    # inclusive.
    start_index = 0
    end_index = len(data)

    # Find the starting index when the year is above the start
    # target if needed.
    if start is not None:
        for i in range(start_index, end_index):
            if data[i]['year'] >= start:
                start_index = i
                break
        else:
            # The start date is after all the elements.
            start_index = len(data)

    # Get the stopping index, the index after the element larger than
    # the end if needed.
    if end is not None:
        for i in range(start_index, end_index):
            if data[i]['year'] > end:
                end_index = i
                break

    return data[start_index:end_index]


def read_data_offset(limit=None, offset=None):
    """Return data from an offset with a limit."""
    data = read_data()

    if offset is None:
        offset = 0
    elif offset < 0:
        raise ValueError('offset must be non-negative')

    if limit is None:
        return data[offset:]
    elif limit < 0:
        raise ValueError('limit must be non-negative')
    else:
        return data[offset:offset + limit]

