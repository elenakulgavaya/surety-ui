import base64
import json
from unittest.mock import MagicMock, patch

import pytest

from selenium.common import WebDriverException

from surety.ui.local_storage import LocalStorage, Command

# pylint: disable=redefined-outer-name

@pytest.fixture
def mock_browser(monkeypatch):
    mock_browser_instance = MagicMock()
    mock_driver = MagicMock()
    mock_browser_instance.driver = mock_driver

    def mock_browser_constructor():
        return mock_browser_instance

    monkeypatch.setattr('surety.ui.local_storage.Browser', mock_browser_constructor)
    return mock_browser_instance


def test_set_item(mock_browser):
    LocalStorage.set_item('key1', 'value1')

    mock_browser.driver.execute_script.assert_called_once()
    call_args = mock_browser.driver.execute_script.call_args[0][0]
    assert 'localStorage.setItem' in call_args

def test_set_item_to_integer(mock_browser):
    LocalStorage.set_item('key1', 1234)

    mock_browser.driver.execute_script.assert_called_once()
    call_args = mock_browser.driver.execute_script.call_args[0][0]
    assert 'localStorage.setItem' in call_args


def test_set_item_to_json(mock_browser):
    LocalStorage.set_item('key1', {'test': 123})

    mock_browser.driver.execute_script.assert_called_once()
    call_args = mock_browser.driver.execute_script.call_args[0][0]
    assert 'localStorage.setItem' in call_args



def test_set_item_with_special_chars(mock_browser):
    LocalStorage.set_item('complex-key_123', 'value with spaces & symbols!')

    mock_browser.driver.execute_script.assert_called_once()


def test_get_item(mock_browser):
    mock_browser.driver.execute_script.return_value = 'stored_value'

    value = LocalStorage.get_item('key1')

    assert value == 'stored_value'
    mock_browser.driver.execute_script.assert_called_once()


def test_get_item_not_exists(mock_browser):
    mock_browser.driver.execute_script.return_value = None

    value = LocalStorage.get_item('nonexistent')

    assert value is None


def test_get_item_json_string(mock_browser):
    json_value = '{"key": "value"}'
    mock_browser.driver.execute_script.return_value = json_value

    value = LocalStorage.get_item('json_key')

    assert value == json_value


def test_remove_item(mock_browser):
    LocalStorage.remove_item('key1')

    mock_browser.driver.execute_script.assert_called_once()
    call_args = mock_browser.driver.execute_script.call_args[0][0]
    assert 'removeItem' in call_args


@patch('surety.ui.local_storage.LocalStorage.run_command')
def test_remove_item_handles_exception(mock_run_command, capsys):
    mock_run_command.side_effect = Exception('Database connection failed')

    LocalStorage.remove_item('test_key')

    # Verify the command was called
    mock_run_command.assert_called_once_with(Command.DELETE, 'test_key')

    # Capture and verify printed output
    captured = capsys.readouterr()
    assert 'FAILED TO CLEAR STORAGE' in captured.out
    assert 'Database connection failed' in captured.out


def test_clear(mock_browser):
    LocalStorage.clear()

    mock_browser.driver.execute_script.assert_called_once()
    call_args = mock_browser.driver.execute_script.call_args[0][0]
    assert 'clear' in call_args


@patch('surety.ui.local_storage.LocalStorage.run_command')
def test_clear_handles_exception(mock_run_command, capsys):
    mock_run_command.side_effect = WebDriverException()

    LocalStorage.clear()

    mock_run_command.assert_called_once_with(Command.CLEAR)

    captured = capsys.readouterr()
    assert 'Local storage is not accessible' in captured.out


def test_multiple_operations_sequence(mock_browser):
    mock_browser.driver.execute_script.side_effect = [
        None,  # set_item
        'value1',  # get_item
        None,  # remove_item
        None,  # clear
    ]

    LocalStorage.set_item('key1', 'value1')
    value = LocalStorage.get_item('key1')
    LocalStorage.remove_item('key1')
    LocalStorage.clear()

    assert value == 'value1'
    assert mock_browser.driver.execute_script.call_count == 4


def test_set_and_get_same_key(mock_browser):
    mock_browser.driver.execute_script.side_effect = [
        None,  # set
        'test_value',  # get
    ]

    LocalStorage.set_item('test_key', 'test_value')
    retrieved = LocalStorage.get_item('test_key')

    assert retrieved == 'test_value'


@patch('surety.ui.local_storage.LocalStorage.set_item')
def test_set_encoded_encodes_and_stores_data(mock_set_item):
    test_data = {'name': 'John', 'age': 30}

    LocalStorage.set_encoded('user_data', test_data)

    mock_set_item.assert_called_once()
    call_args = mock_set_item.call_args[0]
    assert call_args[0] == 'user_data'

    encoded_value = call_args[1]
    decoded_value = json.loads(base64.b64decode(encoded_value))
    assert decoded_value == test_data


@patch('surety.ui.local_storage.LocalStorage.set_item')
def test_set_encoded_handles_complex_data(mock_set_item):
    test_data = {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ],
        'metadata': {'version': '1.0', 'timestamp': 123456}
    }

    LocalStorage.set_encoded('complex_data', test_data)

    mock_set_item.assert_called_once()
    call_args = mock_set_item.call_args[0]
    encoded_value = call_args[1]
    decoded_value = json.loads(base64.b64decode(encoded_value))
    assert decoded_value == test_data


@patch('surety.ui.local_storage.LocalStorage.set_item')
def test_set_encoded_handles_empty_dict(mock_set_item):
    test_data = {}

    LocalStorage.set_encoded('empty', test_data)

    mock_set_item.assert_called_once()
    call_args = mock_set_item.call_args[0]
    encoded_value = call_args[1]
    decoded_value = json.loads(base64.b64decode(encoded_value))
    assert decoded_value == test_data


@patch('surety.ui.local_storage.compare')
@patch('surety.ui.local_storage.LocalStorage.get_item')
def test_verify_decoded_with_matching_data(mock_get_item, mock_compare):
    expected_data = {'name': 'John', 'age': 30}
    encoded_data = base64.b64encode(
        json.dumps(expected_data).encode('utf-8')).decode('utf-8')
    mock_get_item.return_value = encoded_data

    LocalStorage.verify_decoded('user_data', expected_data)

    mock_get_item.assert_called_once_with('user_data')
    mock_compare.assert_called_once_with(
        expected=expected_data,
        actual=expected_data
    )


@patch('surety.ui.local_storage.compare')
@patch('surety.ui.local_storage.LocalStorage.get_item')
def test_verify_decoded_with_none_value(mock_get_item, mock_compare):
    expected_data = {'name': 'John'}
    mock_get_item.return_value = None

    LocalStorage.verify_decoded('missing_key', expected_data)

    mock_get_item.assert_called_once_with('missing_key')
    mock_compare.assert_called_once_with(
        expected=expected_data,
        actual=None
    )


@patch('surety.ui.local_storage.compare')
@patch('surety.ui.local_storage.LocalStorage.get_item')
def test_verify_decoded_with_complex_data(mock_get_item, mock_compare):
    expected_data = {
        'users': [{'id': 1, 'name': 'Alice'}],
        'count': 1
    }
    encoded_data = base64.b64encode(
        json.dumps(expected_data).encode('utf-8')).decode('utf-8')
    mock_get_item.return_value = encoded_data

    LocalStorage.verify_decoded('data', expected_data)

    mock_compare.assert_called_once_with(
        expected=expected_data,
        actual=expected_data
    )


@patch('surety.ui.local_storage.compare')
@patch('surety.ui.local_storage.LocalStorage.get_item')
def test_verify_decoded_decodes_base64_correctly(mock_get_item, mock_compare):
    expected_data = {'status': 'active', 'value': 42}
    encoded_data = base64.b64encode(
        json.dumps(expected_data).encode('utf-8')).decode('utf-8')
    mock_get_item.return_value = encoded_data

    LocalStorage.verify_decoded('test_key', expected_data)

    actual_arg = mock_compare.call_args[1]['actual']
    assert actual_arg == expected_data



@patch('surety.ui.local_storage.compare')
@patch('surety.ui.local_storage.LocalStorage.get_item')
def test_verify_item_with_matching_data(mock_get_item, mock_compare):
    expected_data = {'name': 'Alice', 'age': 25}
    mock_get_item.return_value = json.dumps(expected_data)

    LocalStorage.verify_item('user', expected_data)

    mock_get_item.assert_called_once_with('user')
    mock_compare.assert_called_once_with(
        expected=expected_data,
        actual=expected_data,
        rules=None
    )


@patch('surety.ui.local_storage.compare')
@patch('surety.ui.local_storage.LocalStorage.get_item')
def test_verify_item_with_rules(mock_get_item, mock_compare):
    expected_data = {'name': 'Alice', 'timestamp': 'ANY'}
    actual_data = {'name': 'Alice', 'timestamp': 123456}
    mock_get_item.return_value = json.dumps(actual_data)

    custom_rules = {'timestamp': lambda x: isinstance(x, int)}

    LocalStorage.verify_item('user', expected_data, rules=custom_rules)

    mock_get_item.assert_called_once_with('user')
    mock_compare.assert_called_once_with(
        expected=expected_data,
        actual=actual_data,
        rules=custom_rules
    )


@patch('surety.ui.local_storage.compare')
@patch('surety.ui.local_storage.LocalStorage.get_item')
def test_verify_item_with_none_value(mock_get_item, mock_compare):
    expected_data = {'name': 'Bob'}
    mock_get_item.return_value = None

    LocalStorage.verify_item('missing', expected_data)

    mock_get_item.assert_called_once_with('missing')
    mock_compare.assert_called_once_with(
        expected=expected_data,
        actual=None,
        rules=None
    )


@patch('surety.ui.local_storage.compare')
@patch('surety.ui.local_storage.LocalStorage.get_item')
def test_verify_item_with_empty_dict(mock_get_item, mock_compare):
    expected_data = {}
    mock_get_item.return_value = json.dumps({})

    LocalStorage.verify_item('empty', expected_data)

    mock_compare.assert_called_once_with(
        expected=expected_data,
        actual={},
        rules=None
    )


@patch('surety.ui.local_storage.compare')
@patch('surety.ui.local_storage.LocalStorage.get_item')
def test_verify_item_parses_json_correctly(mock_get_item, mock_compare):
    expected_data = {'items': [1, 2, 3], 'total': 3}
    json_string = json.dumps(expected_data)
    mock_get_item.return_value = json_string

    LocalStorage.verify_item('data', expected_data)

    actual_arg = mock_compare.call_args[1]['actual']
    assert actual_arg == expected_data
    assert isinstance(actual_arg, dict)


@patch('surety.ui.local_storage.compare')
@patch('surety.ui.local_storage.LocalStorage.get_item')
def test_verify_item_with_list_data(mock_get_item, mock_compare):
    expected_data = [1, 2, 3, 4, 5]
    mock_get_item.return_value = json.dumps(expected_data)

    LocalStorage.verify_item('numbers', expected_data)

    mock_compare.assert_called_once_with(
        expected=expected_data,
        actual=expected_data,
        rules=None
    )
