import os

import redis

import jobs


redis_client = redis.StrictRedis(host=os.environ['REDIS_HOST'],
                                 port=os.environ['REDIS_PORT'],
                                 db=os.environ['REDIS_DB'])


def start_worker():
    """Handle new job ids as they come in.

    Note that this function will block while it is still listening to
    new job ids.
    """
    while True:
        job_id = jobs.get_new_job(redis_client)
        job_dict = jobs.get_job(redis_client, job_id)

        _handle_new_job(job_dict)


def _handle_new_job(job_dict):
    print('TODO: actually do something here')
