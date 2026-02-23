import pytest

from unittest.mock import MagicMock
from surety.ui.indexed_db import IndexedDb


@pytest.fixture
def mock_browser(monkeypatch):
    mock_browser_instance = MagicMock()
    mock_driver = MagicMock()
    mock_browser_instance.driver = mock_driver

    def mock_browser_constructor():
        return mock_browser_instance

    monkeypatch.setattr('surety.ui.indexed_db.Browser', mock_browser_constructor)
    return mock_browser_instance


def test_indexed_db_initialization():
    db = IndexedDb('test_db')
    assert db.name == 'test_db'


def test_get_all_records(mock_browser):
    mock_browser.driver.execute_script.return_value = [
        {'id': 1, 'name': 'Record 1'},
        {'id': 2, 'name': 'Record 2'},
    ]

    db = IndexedDb('test_db')
    records = db.get_all_records('table1')

    assert len(records) == 2
    assert records[0]['id'] == 1
    mock_browser.driver.execute_script.assert_called_once()


def test_get_all_records_empty(mock_browser):
    mock_browser.driver.execute_script.return_value = []

    db = IndexedDb('test_db')
    records = db.get_all_records('empty_table')

    assert records == []


def test_delete_all_records(mock_browser):
    mock_browser.driver.execute_script.return_value = None

    db = IndexedDb('test_db')
    db.delete_all_records('table1')

    mock_browser.driver.execute_script.assert_called_once()


def test_insert_record(mock_browser):
    mock_browser.driver.execute_script.return_value = 1

    db = IndexedDb('test_db')
    record_json = '{"id": 1, "name": "New Record"}'
    result = db.insert_record('table1', record_json)

    assert result == 1
    mock_browser.driver.execute_script.assert_called_once()


def test_indexed_db_multiple_operations(mock_browser):
    mock_browser.driver.execute_script.side_effect = [
        [{'id': 1}],  # get_all_records
        None,  # delete_all_records
        1,  # insert_record
    ]

    db = IndexedDb('test_db')

    records = db.get_all_records('table1')
    assert records == [{'id': 1}]

    db.delete_all_records('table1')

    result = db.insert_record('table1', '{"id": 1}')
    assert result == 1

    assert mock_browser.driver.execute_script.call_count == 3
