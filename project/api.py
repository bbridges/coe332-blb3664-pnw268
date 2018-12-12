import os
import io

from flask import Flask, jsonify, request, send_file
import redis

import csv_parser
import jobs


redis_client = redis.StrictRedis(host=os.environ['REDIS_HOST'],
                                 port=os.environ['REDIS_PORT'],
                                 db=os.environ['REDIS_DB'])
app = Flask(__name__)


@app.route('/spots', methods=['GET'])
def spots_index():
    """Return the sunspots data over a range or offset."""
    start = request.args.get('start')
    end = request.args.get('end')
    limit = request.args.get('limit')
    offset = request.args.get('offset')

    is_range_case = start is not None or end is not None
    is_offset_case = limit is not None or offset is not None

    if is_range_case and is_offset_case:
        return _make_error(
            'limit and/or offset cannot be combined with start and/or end'
        ), 400
    elif is_range_case:
        return _handle_range_case(start, end)
    elif is_offset_case:
        return _handle_offset_case(limit, offset)
    else:
        data = csv_parser.read_data()
        return jsonify(data)


def _handle_range_case(start, end):
    # Converting the start and end to integers if they were
    # provided.
    try:
        # These conversions might fail if they aren't None or
        # integer strings.
        if start is not None:
            start = int(start)
        if end is not None:
            end = int(end)
    except ValueError:
        return _make_error(
            'start and end, if provided, must be integers.'
        ), 400
    else:
        data = csv_parser.read_data_range(start=start, end=end)
        return jsonify(data)


def _handle_offset_case(limit, offset):
    # Converting the limit and offset to integers if they were
    # provided and checking if they are non-negative.
    try:
        # These conversions might fail if they aren't None or
        # integer strings.
        if limit is not None:
            limit = int(limit)
        if offset is not None:
            offset = int(offset)
    except ValueError:
        return _make_error(
            'limit and offset, if provided, must be integers.'
        ), 400
    else:
        if (limit is not None and limit < 0) or \
                (offset is not None and offset < 0):
            return _make_error(
                'limit and offset, if provided, must be non-negative'
            ), 400
        else:
            data = csv_parser.read_data_offset(limit=limit, offset=offset)
            return jsonify(data)


@app.route('/spots/<id>', methods=['GET'])
def spots_id(id):
    """Return a sunpots data row by id."""
    # Turn the id into an integer if it's non-negative, otherwise
    # return an error.
    try:
        # Might fail if it's not an integer.
        id = int(id)

        # Fail it also if it's below zero.
        if id < 0:
            raise ValueError
    except ValueError:
        return _make_error('invalid value provided for row id.'), 400

    data = csv_parser.read_data_offset(offset=id, limit=1)

    if len(data) == 1:
        return jsonify(data[0])
    else:
        return _make_error('row not found for row id.'), 404


@app.route('/spots/year/<year>', methods=['GET'])
def spots_year(year):
    """Return the value by id."""
    # Turn the year into an integer. Unlike the id, it's technically
    # alright if the year is negative, it's just that this dataset
    # doesn't have any negative years in the rows.
    try:
        # Might fail if it's not an integer.
        year = int(year)
    except ValueError:
        return _make_error('invalid value provided for year.'), 400

    data = csv_parser.read_data_range(start=year, end=year)

    if len(data) == 1:
        return jsonify(data[0])
    else:
        return _make_error('row not found for year.'), 404


@app.route('/jobs', methods=['POST', 'GET'])
def jobs_index():
    """Handle the root jobs collection."""

    if request.method == 'POST':
        # Parse if this is a range or offset case (or neither), and
        # send an error to the client if they chose both.
        try:
            body = request.get_json(force=True) or {}
        except Exception as e:
            return _make_error(f'Invalid JSON: {e}'), 400

        start = body.get('start')
        end = body.get('end')
        limit = body.get('limit')
        offset = body.get('offset')

        is_range_case = start is not None or end is not None
        is_offset_case = limit is not None or offset is not None

        if is_range_case and is_offset_case:
            return _make_error(
                'limit and/or offset cannot be combined with start and/or end'
            ), 400
        elif is_range_case:
            return _handle_post_range_job(start, end)
        elif is_offset_case:
            return _handle_post_offset_job(limit, offset)
        else:
            job_dict = jobs.create_job(redis_client)
            return jsonify(job_dict)
    elif request.method == 'GET':
        job_dicts = jobs.get_all_jobs(redis_client)
        return jsonify(job_dicts)


def _handle_post_range_job(start, end):
    # Converting the start and end to integers if they were
    # provided.
    try:
        # These conversions might fail if they aren't None or
        # integer strings.
        if start is not None:
            start = int(start)
        if end is not None:
            end = int(end)
    except ValueError:
        return _make_error(
            'start and end, if provided, must be integers.'
        ), 400
    else:
        job_dict = jobs.create_job(redis_client, start=start, end=end)
        return jsonify(job_dict)


def _handle_post_offset_job(limit, offset):
    # Converting the limit and offset to integers if they were
    # provided and checking if they are non-negative.
    try:
        # These conversions might fail if they aren't None or
        # integer strings.
        if limit is not None:
            limit = int(limit)
        if offset is not None:
            offset = int(offset)
    except ValueError:
        return _make_error(
            'limit and offset, if provided, must be integers.'
        ), 400
    else:
        job_dict = jobs.create_job(redis_client, limit=limit, offset=offset)
        return jsonify(job_dict)


@app.route('/jobs/<id>', methods=['GET'])
def job_by_id(id):
    """Return a job by id."""
    job_dict = jobs.get_job(redis_client, id)

    if job_dict:
        return jsonify(job_dict)
    else:
        return _make_error('job not found for job id.'), 404


@app.route('/jobs/<id>/plot', methods=['GET'])
def job_plot(id):
    """Return a plot for a job by job id."""
    plot = jobs.get_plot(redis_client, id)

    if plot:
        return send_file(io.BytesIO(plot), mimetype='image/png',
                         as_attachment=True, attachment_filename=f'{id}.png')
    else:
        return _make_error('plot not found for job id.'), 404


# Format a simple JSON error message.
def _make_error(message):
    return jsonify(status='Error', message=message)
