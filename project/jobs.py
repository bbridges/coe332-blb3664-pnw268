"""Functions for working with jobs.

Note that the redis client objects must be passed into the functions
to allow for easier testing via dependency injection and more
explicit management of the redis clients in the api (and future
worker).
"""

from datetime import datetime
import uuid


def create_job(redis_client, start=None, end=None):
    """Create a job on Redis with optional start and end times.

    Returns the job dict.
    """
    job_id = _generate_id()
    time_str = _get_iso_time()

    job_dict = _job_dict(job_id, 'submitted', start, end, time_str, time_str)
    key = _format_key(job_id)

    _save_job_redis(redis_client, key, job_dict)
    _queue_job_redis(redis_client, key)

    return job_dict


def get_all_jobs(redis_client):
    """Get all jobs.

    This fetches all the job keys, and then gets all the all the jobs
    in a transaction, and finally converts them to UTF-8 encoded
    dictionaries.
    """
    all_keys = redis_client.smembers('job-keys')

    pipe = redis_client.pipeline()

    for key in all_keys:
        pipe.hgetall(key)

    job_hashes = pipe.execute()

    return [_convert_job_hash(job_hash) for job_hash in job_hashes]


def get_job(redis_client, job_id):
    """Get a job by its id.

    Returns None if the job doesn't exist.
    """
    key = _format_key(job_id)
    job_hash = redis_client.hgetall(key)

    if job_hash:
        return _convert_job_hash(job_hash)
    else:
        return None


def get_new_job(redis_client):
    """Return the next new job id.

    This function will block until it is returned.
    """
    return redis_client.brpop('new-jobs')


def _get_iso_time():
    """Get the current time in ISO 8601."""
    return datetime.utcnow().isoformat()


def _generate_id():
    """Generate a UUID4 ID."""
    return str(uuid.uuid4())


def _job_dict(id, status, start, end, created_at, last_updated):
    """Returns a dictionary representing a job."""
    return {
        'id': id,
        'status': status,
        'start': start,
        'end': end,
        'created_at': created_at,
        'last_updated': last_updated
    }


def _format_key(id):
    """Format a job id for redis."""
    return f'job.{id}'


def _save_job_redis(redis_client, key, job_dict):
    """Save a job with a redis client.

    This also adds the key to the jobs-key set so it can be looked
    up with all other jobs.
    """
    pipe = redis_client.pipeline()

    pipe.sadd('job-keys', key)
    pipe.hmset(key, job_dict)

    pipe.execute()


def _queue_job_redis(redis_client, key):
    """Queue an id to be processed."""
    redis_client.lpush('new-jobs', key)


def _convert_job_hash(job_hash):
    """Convert a job hash to a job dict."""
    return _job_dict(
        job_hash[b'id'].decode(),
        job_hash[b'status'].decode(),
        _parse_redis_number(job_hash[b'start']),
        _parse_redis_number(job_hash[b'end']),
        job_hash[b'created_at'].decode(),
        job_hash[b'last_updated'].decode()
    )


def _parse_redis_number(value):
    return int(value) if value != b'None' else None
