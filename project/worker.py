import io
import os
import random

import matplotlib.pyplot as plt
import redis
import requests

import jobs


redis_client = redis.StrictRedis(host=os.environ['REDIS_HOST'],
                                 port=os.environ['REDIS_PORT'],
                                 db=os.environ['REDIS_DB'])

API_BASE = f"http://{os.environ['API_HOST']}:{os.environ['API_PORT']}"
TXT_FILE = os.path.join(os.path.dirname(__file__), 'fun_facts.txt')


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

    plot = _create_plot(data, job_dict['job_type'])
    jobs.update_plot(redis_client, job_id, plot)

    jobs.update_status(redis_client, job_id, 'completed')


def _get_data(job_dict):
    fields = ('start', 'end', 'limit', 'offset')
    params = {field: job_dict.get(field) for field in fields
              if job_dict.get(field) is not None}
    return requests.get(f'{API_BASE}/spots', params=params).json()

def _create_plot(data, job_type):
    # line, histogram, box_plot, fun_facts

    if job_type == 'line':
        _create_line_graph(data)
    elif job_type == 'fun_facts':
        _create_fun_graph(data)
    elif job_type == 'histogram':
        _create_histogram(data)
    elif job_type == 'box_plot':
        _create_box_plot(data)
    
    file = io.BytesIO()
    plt.savefig(file)

    plt.close()

    return file.getvalue()


def _create_line_graph(data):
    """Create a line graph for given range."""

    spots = [row['spots'] for row in data]
    year = [row['year'] for row in data]

    plt.plot(year, spots, color='red')
    plt.title('Line Graph of Sunspots')
    plt.xlabel('Year')
    plt.ylabel('Number of Spots')


def _create_fun_graph(data):
    """Create a line graph with sunspot fun facts."""

    # Possible units of conversion for # of sunspots.
    units = [{'Name': 'bakers dozens', 'Units':  1 / 13},
             {'Name': 'dozens', 'Units': 1 / 12},
             {'Name': 'scores', 'Units': 1 / 20},
             {'Name': 'grosses', 'Units': 1 / 144},
             {'Name': 'googols', 'Units': 10 ** (-100)}]

    random_unit = random.randint(0, 4)
    spots = [row['spots'] for row in data]
    year = [row['year'] for row in data]

    # Create the fun fact string.
    fun_fact = ('Did you know?\n\n' +
                 read_fun_data() +
                 '\n\n'
                'The maximum number of spots during this time period' 
                'was equal to  ' +
                 str(max(spots) * units[random_unit]['Units']) + 
                 ' ' + 
                 units[random_unit]['Name'] + '.')

    plt.plot(year, spots)
    plt.grid(b=True)
    plt.title('Fun Graph of Sunspots')
    plt.xlabel('Year')
    plt.ylabel('Number of Spots')
    plt.axis([min(year), max(year), min(spots), max(spots)])

    # Define properties of box surrounding fun fact.
    bbox_props = dict(boxstyle="round,pad=0.3", fc="cyan", 
                      ec="b", lw=2, alpha=0.5)
    plt.text(year[0], max(spots) * 0.6, fun_fact, bbox=bbox_props, wrap=True)


def _create_histogram(data):
    """Create a histogram for given range."""

    spots = [row['spots'] for row in data]

    plt.hist(spots, bins=15, color='red')
    plt.title('Histogram of Sunspots')
    plt.xlabel('Number of Spots in a Year')
    plt.ylabel('Frequency')


def _create_box_plot(data):
    """Create a box plot for given range."""

    spots = [row['spots'] for row in data]

    plt.boxplot(spots, vert=False)
    plt.title('Box Plot of Sunspots')
    plt.xlabel('Number of Sunspots in One Year')


def read_fun_data():
    """Return a random fun fact from file."""

    fun_data = []

    # Read all fun facts.
    with open(TXT_FILE, 'r') as f:
        for i, line in enumerate(f):
            if i > 3:
                fun_data.append(line)

    # Return a random fun fact each time.
    return fun_data[random.randint(0, 13)]
