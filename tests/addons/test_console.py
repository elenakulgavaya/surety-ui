from unittest.mock import patch

import pytest

from surety.ui.pytest_addons import get_console_errors, check_console_errors


@patch('surety.ui.pytest_addons.Cfg')
@patch('surety.ui.pytest_addons.Browser')
def test_get_console_errors_returns_all(mock_browser, mock_cfg):
    mock_cfg.Browser.get.return_value = None
    mock_browser.return_value.console_log = [
        {'message': 'Error 1'},
        {'message': 'Error 2'}
    ]

    result = get_console_errors()

    assert len(result) == 2
    assert result[0]['message'] == 'Error 1'
    assert result[1]['message'] == 'Error 2'


@patch('surety.ui.pytest_addons.Cfg')
@patch('surety.ui.pytest_addons.Browser')
def test_get_console_errors_filters_excluded(mock_browser, mock_cfg):
    mock_cfg.Browser.get.return_value = ['excluded_text']
    mock_browser.return_value.console_log = [
        {'message': 'Error with excluded_text'},
        {'message': 'Error without exclusion'}
    ]

    result = get_console_errors()

    assert len(result) == 1
    assert result[0]['message'] == 'Error without exclusion'


@patch('surety.ui.pytest_addons.Cfg')
@patch('surety.ui.pytest_addons.Browser')
def test_get_console_errors_filters_multiple(mock_browser, mock_cfg):
    mock_cfg.Browser.get.return_value = ['excluded1', 'excluded2']
    mock_browser.return_value.console_log = [
        {'message': 'Error with excluded1'},
        {'message': 'Error with excluded2'},
        {'message': 'Valid error'}
    ]

    result = get_console_errors()

    assert len(result) == 1
    assert result[0]['message'] == 'Valid error'


@patch('surety.ui.pytest_addons.Cfg')
@patch('surety.ui.pytest_addons.Browser')
def test_get_console_errors_no_errors(mock_browser, mock_cfg):
    mock_cfg.Browser.get.return_value = None
    mock_browser.return_value.console_log = []

    result = get_console_errors()

    assert result == []


@patch('surety.ui.pytest_addons.get_console_errors')
def test_check_console_errors_passes(mock_get_errors):
    mock_get_errors.return_value = []

    @check_console_errors
    def test_func():
        pass

    test_func()


@patch('surety.ui.pytest_addons.get_console_errors')
def test_check_console_errors_fails(mock_get_errors):
    mock_get_errors.return_value = [
        {'message': 'Console error'}
    ]

    @check_console_errors
    def test_func():
        pass

    with pytest.raises(AssertionError, match='Console log errors'):
        test_func()


@patch('surety.ui.pytest_addons.get_console_errors')
def test_check_console_errors_preserves_function_execution(mock_get_errors):
    mock_get_errors.return_value = []
    executed = []

    @check_console_errors
    def test_func():
        executed.append(True)

    test_func()

    assert executed == [True]


@patch('surety.ui.pytest_addons.get_console_errors')
def test_check_console_errors_preserves_function_metadata(mock_get_errors):
    mock_get_errors.return_value = []

    @check_console_errors
    def test_func():
        """Test docstring"""

    assert test_func.__name__ == 'test_func'
    assert test_func.__doc__ == 'Test docstring'
