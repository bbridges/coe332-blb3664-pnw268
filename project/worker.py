import os
import io

import redis
import requests

import jobs


redis_client = redis.StrictRedis(host=os.environ['REDIS_HOST'],
                                 port=os.environ['REDIS_PORT'],
                                 db=os.environ['REDIS_DB'])

API_BASE = f"http://{os.environ['API_HOST']}:{os.environ['API_PORT']}"


def start_worker():
    """Handle new job ids as they come in.

    Note that this function will block while it is still listening to
    new job ids.
    """
    while True:
        job_id = jobs.get_new_job(redis_client)
        _handle_job_id(job_id)


def _handle_job_id(job_id):
    jobs.update_status(redis_client, job_id, 'processing')

    job_dict = jobs.get_job(redis_client, job_id)
    data = _get_data(job_dict)

    plot = _create_plot(data)
    jobs.update_plot(redis_client, job_id, plot)

    jobs.update_status(redis_client, job_id, 'completed')


def _get_data(job_dict):
    fields = ('start', 'end', 'limit', 'offset')
    params = {field: job_dict.get(field) for field in fields
              if job_dict.get(field) is not None}
    return requests.get(f'{API_BASE}/spots', params=params).json()


def _create_plot(data):
    file = io.BytesIO()

    # TODO: do all the plotting stuff here and save to the BytesIO
    #       object above.
    file.write(b'todo')

    return file.getvalue()
