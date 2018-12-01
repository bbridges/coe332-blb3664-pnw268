import os.path
import sys

import pytest


sys.path.append(os.path.join(os.path.dirname(__file__), '../project'))


import csv_parser


def test_read_data_types():
    data = csv_parser.read_data()

    # This should give a list.
    assert type(data) == list

    # Each element should be a dictionary with three integer keys.
    for row in data:
        assert len(row.keys()) == 3

        for key in ('id', 'year', 'spots'):
            assert type(row[key]) == int


def test_read_data_count():
    data = csv_parser.read_data()

    # 100 elements should be returned.
    assert len(data) == 100


def test_read_data_values():
    data = csv_parser.read_data()

    # Checking the first and last values
    assert data[0]['id'] == 0
    assert data[0]['year'] == 1770
    assert data[0]['spots'] == 101
    assert data[-1]['id'] == 99
    assert data[-1]['year'] == 1869
    assert data[-1]['spots'] == 74


def test_read_data_range_types():
    data = csv_parser.read_data_range()

    # This should give a list.
    assert type(data) == list

    # Each element should be a dictionary with three integer keys.
    for row in data:
        assert len(row.keys()) == 3

        for key in ('id', 'year', 'spots'):
            assert type(row[key]) == int


def test_read_data_range_no_args():
    data = csv_parser.read_data_range()

    # The entire series should be returned when no args are passed.
    assert len(data) == 100


def test_read_data_range_only_start():
    data = csv_parser.read_data_range(1800)

    # Check the first and last years when only the start is given.
    assert data[0]['year'] == 1800
    assert data[-1]['year'] == 1869


def test_read_data_range_only_end():
    data = csv_parser.read_data_range(end=1800)

    # Check the first and last years when only the end is given.
    assert data[0]['year'] == 1770
    assert data[-1]['year'] == 1800


def test_read_data_range_both_args():
    data = csv_parser.read_data_range(1795, 1805)

    # Check the first and last years when both args are passed.
    assert data[0]['year'] == 1795
    assert data[-1]['year'] == 1805


def test_read_data_range_start_after_end():
    data = csv_parser.read_data_range(1805, 1795)

    # No entries should exist if the start is after the end.
    assert len(data) == 0


def test_read_data_range_start_is_end():
    data = csv_parser.read_data_range(1800, 1800)

    # 1 entry should exist if the start is the same as the end.
    assert len(data) == 1


def test_read_data_range_outside_range():
    data = csv_parser.read_data_range(1600, 1900)

    # All entries should be returned when the start and end are
    # outside of the year range.
    assert len(data) == 100


def test_read_data_offset_types():
    data = csv_parser.read_data_offset()

    # This should give a list.
    assert type(data) == list

    # Each element should be a dictionary with three integer keys.
    for row in data:
        assert len(row.keys()) == 3

        for key in ('id', 'year', 'spots'):
            assert type(row[key]) == int


def test_read_data_offset_no_args():
    data = csv_parser.read_data_offset()

    # The entire series should be returned when no args are passed.
    assert len(data) == 100


def test_read_data_offset_only_limit():
    data = csv_parser.read_data_offset(50)

    # Check the length and first and last ids when only the limit is
    # given.
    assert len(data) == 50
    assert data[0]['id'] == 0
    assert data[-1]['id'] == 49


def test_read_data_offset_only_offset():
    data = csv_parser.read_data_offset(offset=10)

    # Check the length and first and last ids when only the offset is
    # given.
    assert len(data) == 90
    assert data[0]['id'] == 10
    assert data[-1]['id'] == 99


def test_read_data_offset_both_args():
    data = csv_parser.read_data_offset(5, 10)

    # Check the length and first and last ids when both args are
    # passed.
    assert len(data) == 5
    assert data[0]['id'] == 10
    assert data[-1]['id'] == 14


def test_read_data_offset_large_limit():
    data = csv_parser.read_data_offset(110, 10)

    # All entries after 10 should be returned when the limit exceeds
    # the number of items left the dataset.
    assert len(data) == 90
    assert data[0]['id'] == 10
    assert data[-1]['id'] == 99


def test_read_data_offset_large_offset():
    data = csv_parser.read_data_offset(10, 150)

    # No entries should exist if the offset is after the end.
    assert len(data) == 0


def test_read_data_offset_zero_limit():
    data = csv_parser.read_data_offset(0, 10)

    # Nothing should be returned with a limit of zero.
    assert len(data) == 0


def test_read_data_offset_zero_offset():
    data = csv_parser.read_data_offset(10, 0)

    # Entry ids shouldn't change when the offset is zero.
    assert len(data) == 10
    assert data[0]['id'] == 0
    assert data[-1]['id'] == 9


def test_read_data_offset_negative_limit_throws():
    # A ValueError is thrown when using a negative limit.
    with pytest.raises(ValueError):
        csv_parser.read_data_offset(-1, 10)


def test_read_data_offset_negative_offset_throws():
    # A ValueError is thrown when using a negative offset.
    with pytest.raises(ValueError):
        csv_parser.read_data_offset(1, -10)
