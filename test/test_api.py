import requests


URL_BASE = 'http://localhost:5000'


def test_index_status_code():
    res = requests.get(URL_BASE + '/spots')

    assert res.status_code == 200


def test_index_data_types():
    # Will error if not JSON.
    data = requests.get(URL_BASE + '/spots').json()

    # This should give a list.
    assert type(data) == list

    # Each element should be a dictionary with three integer keys.
    for row in data:
        assert len(row.keys()) == 3

        for key in ('id', 'year', 'spots'):
            assert type(row[key]) == int


def test_index_data_count():
    data = requests.get(URL_BASE + '/spots').json()

    # 100 elements should be returned.
    assert len(data) == 100


def test_index_data_values():
    data = requests.get(URL_BASE + '/spots').json()

    # Checking the first and last values
    assert data[0]['id'] == 0
    assert data[0]['year'] == 1770
    assert data[0]['spots'] == 101
    assert data[-1]['id'] == 99
    assert data[-1]['year'] == 1869
    assert data[-1]['spots'] == 74


def test_index_start_before_end():
    res = requests.get(URL_BASE + '/spots?start=1800&end=1805')

    assert res.status_code == 200

    data = res.json()

    assert type(data) == list
    assert len(data) == 6


def test_index_only_start():
    res = requests.get(URL_BASE + '/spots?start=1865')

    assert res.status_code == 200

    data = res.json()

    assert type(data) == list
    assert len(data) == 5


def test_index_only_end():
    res = requests.get(URL_BASE + '/spots?end=1865')

    assert res.status_code == 200

    data = res.json()

    assert type(data) == list
    assert len(data) == 96


def test_index_start_after_end():
    res = requests.get(URL_BASE + '/spots?start=1870&end=1865')

    assert res.status_code == 200

    data = res.json()

    assert type(data) == list
    assert len(data) == 0


def test_index_limit_and_offset():
    res = requests.get(URL_BASE + '/spots?limit=30&offset=90')

    assert res.status_code == 200

    data = res.json()

    assert type(data) == list
    assert len(data) == 10


def test_index_limit():
    res = requests.get(URL_BASE + '/spots?limit=30')

    assert res.status_code == 200

    data = res.json()

    assert type(data) == list
    assert len(data) == 30


def test_index_offset():
    res = requests.get(URL_BASE + '/spots?offset=30')

    assert res.status_code == 200

    data = res.json()

    assert type(data) == list
    assert len(data) == 70


def test_index_invalid_start():
    res = requests.get(URL_BASE + '/spots?start=abc')

    assert res.status_code == 400

    data = res.json()

    # Note: Not testing the contents of the error message because
    # that would tie this test too closely to the implementation.
    # Instead, this just asserts that a message does indeed exist.
    assert data['status'] == 'Error'
    assert len(data['message']) >= 1


def test_index_invalid_end():
    res = requests.get(URL_BASE + '/spots?end=abc')

    assert res.status_code == 400

    data = res.json()

    assert data['status'] == 'Error'
    assert len(data['message']) >= 1


def test_index_invalid_limit():
    res = requests.get(URL_BASE + '/spots?limit=-1')

    assert res.status_code == 400

    data = res.json()

    assert data['status'] == 'Error'
    assert len(data['message']) >= 1


def test_index_invalid_offset():
    res = requests.get(URL_BASE + '/spots?offset=-10')

    assert res.status_code == 400

    data = res.json()

    assert data['status'] == 'Error'
    assert len(data['message']) >= 1


def test_index_start_and_offset():
    res = requests.get(URL_BASE + '/spots?start=1800&offset=1')

    assert res.status_code == 400

    data = res.json()

    assert data['status'] == 'Error'
    assert len(data['message']) >= 1


def test_by_id_status_code():
    res = requests.get(URL_BASE + '/spots/5')

    assert res.status_code == 200


def test_by_id_data_types():
    # Will error if not JSON.
    data = requests.get(URL_BASE + '/spots/5').json()

    # This should give a dictionary.
    assert type(data) == dict

    # The dictionary should have three integer keys.
    assert len(data.keys()) == 3

    for key in ('id', 'year', 'spots'):
        assert type(data[key]) == int


def test_by_id_expected_id():
    data = requests.get(URL_BASE + '/spots/5').json()

    assert data['id'] == 5


def test_by_year_status_code():
    res = requests.get(URL_BASE + '/spots/year/1800')

    assert res.status_code == 200


def test_by_year_data_types():
    # Will error if not JSON.
    data = requests.get(URL_BASE + '/spots/year/1800').json()

    # This should give a dictionary.
    assert type(data) == dict

    # The dictionary should have three integer keys.
    assert len(data.keys()) == 3

    for key in ('id', 'year', 'spots'):
        assert type(data[key]) == int


def test_by_year_expected_id_and_year():
    data = requests.get(URL_BASE + '/spots/year/1800').json()

    assert data['id'] == 30
    assert data['year'] == 1800
