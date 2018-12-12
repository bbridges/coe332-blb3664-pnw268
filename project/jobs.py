"""Functions for working with jobs.

Note that the redis client objects must be passed into the functions
to allow for easier testing via dependency injection and more
explicit management of the redis clients in the api (and future
worker).
"""

from datetime import datetime
import uuid


def create_job(redis_client, start=None, end=None, limit=None, offset=None):
    """Create a job on Redis with optional data query params.

    Returns the job dict.
    """
    job_id = _generate_id()
    time_str = _get_iso_time()

    job_dict = _job_dict(job_id, 'submitted', start, end, limit, offset,
                         time_str, time_str, False)

    _save_job_redis(redis_client, job_id, job_dict)
    _queue_job_redis(redis_client, job_id)

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


def get_plot(redis_client, job_id):
    """Get a plot by its associated job id.

    Returns None if the plot doesn't exist.
    """
    key = _format_plot_key(job_id)
    return redis_client.get(key)


def get_new_job(redis_client):
    """Return the next new job id.

    This function will block until it is returned.
    """
    return redis_client.brpop('new-jobs')[1].decode()


def update_status(redis_client, job_id, status):
    """Update the status for a job."""
    _update_job_redis(redis_client, job_id, status=status)


def update_plot(redis_client, job_id, plot):
    """Add a plot to an existing job.

    The plot is stored as a binary separate from the job hash.
    """
    _save_plot_redis(redis_client, job_id, plot=plot)
    _update_job_redis(redis_client, job_id, has_plot=True)


def _get_iso_time():
    """Get the current time in ISO 8601."""
    return datetime.utcnow().isoformat()


def _generate_id():
    """Generate a UUID4 ID."""
    return str(uuid.uuid4())


def _job_dict(job_id, status, start, end, limit, offset, created_at,
              last_updated, has_plot):
    """Returns a dictionary representing a job."""
    return {
        'id': job_id,
        'status': status,
        'start': start,
        'end': end,
        'limit': limit,
        'offset': offset,
        'created_at': created_at,
        'last_updated': last_updated,
        'has_plot': has_plot
    }


def _format_key(job_id):
    """Format a job id for redis."""
    return f'job.{job_id}'


def _format_plot_key(job_id):
    """Format a plot key from a job id."""
    return f'plot.{job_id}'


def _save_job_redis(redis_client, job_id, job_dict):
    """Save a job with a redis client.

    This also adds the key to the jobs-key set so it can be looked
    up with all other jobs.
    """
    key = _format_key(job_id)

    pipe = redis_client.pipeline()

    pipe.sadd('job-keys', key)
    pipe.hmset(key, job_dict)

    pipe.execute()


def _save_plot_redis(redis_client, job_id, plot):
    """Save a plot separate from a job."""
    key = _format_plot_key(job_id)
    redis_client.set(key, plot)


def _update_job_redis(redis_client, job_id, **kwargs):
    """Update a job dict on Redis."""
    key = _format_key(job_id)
    kwargs.setdefault('last_updated', _get_iso_time())

    redis_client.hmset(key, kwargs)


def _queue_job_redis(redis_client, key):
    """Queue an id to be processed."""
    redis_client.lpush('new-jobs', key)


def _convert_job_hash(job_hash):
    """Convert a job hash to a job dict."""
    _redis_string = lambda value: value.decode() if value != b'None' else None
    _redis_number = lambda value: int(value) if value != b'None' else None
    _redis_boolean = lambda value: value == b'True'

    return _job_dict(
        _redis_string(job_hash[b'id']),
        _redis_string(job_hash[b'status']),
        _redis_number(job_hash[b'start']),
        _redis_number(job_hash[b'end']),
        _redis_number(job_hash[b'limit']),
        _redis_number(job_hash[b'offset']),
        _redis_string(job_hash[b'created_at']),
        _redis_string(job_hash[b'last_updated']),
        _redis_boolean(job_hash[b'has_plot'])
    )
