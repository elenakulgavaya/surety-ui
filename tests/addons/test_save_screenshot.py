from unittest.mock import Mock, patch
from selenium.common.exceptions import WebDriverException

from surety.ui.pytest_addons import (
    is_screenshot_marked, save_screenshot_on_failure,
)



def test_is_screenshot_marked():
    item = Mock()
    marker = Mock()
    marker.name = 'screenshot'
    item.own_markers = [marker]

    result = is_screenshot_marked(item)

    assert result is True


def test_is_screenshot_not_marked():
    item = Mock()
    marker = Mock()
    marker.name = 'other_marker'
    item.own_markers = [marker]

    result = is_screenshot_marked(item)

    assert result is False


def test_is_screenshot_no_markers():
    item = Mock()
    item.own_markers = []

    result = is_screenshot_marked(item)

    assert result is False


@patch('surety.ui.pytest_addons.Browser')
@patch('surety.ui.pytest_addons.folder.generate_file_name')
@patch('surety.ui.pytest_addons.folder.generate_file_path')
def test_save_screenshot_call(mock_generate_path, mock_generate_name,
                              mock_browser):
    outcome = Mock()
    report = Mock()
    report.failed = True
    report.when = 'call'
    outcome.get_result.return_value = report

    item = Mock()
    item.name = 'test_example'
    item.own_markers = []

    mock_browser.return_value.is_open = True
    mock_driver = Mock()
    mock_browser.return_value.driver = mock_driver
    mock_generate_name.return_value = 'screenshot.png'
    mock_generate_path.return_value = '/path/to/screenshot.png'

    save_screenshot_on_failure(outcome, item)

    mock_generate_name.assert_called_once_with('test_example')
    mock_generate_path.assert_called_once_with('screenshots', 'screenshot.png')
    mock_driver.save_screenshot.assert_called_once_with('/path/to/screenshot.png')


@patch('surety.ui.pytest_addons.Browser')
@patch('surety.ui.pytest_addons.folder.generate_file_name')
@patch('surety.ui.pytest_addons.folder.generate_file_path')
def test_save_screenshot_on_setup_failure(mock_generate_path,
                                          mock_generate_name, mock_browser):
    outcome = Mock()
    report = Mock()
    report.failed = True
    report.when = 'setup'
    outcome.get_result.return_value = report

    item = Mock()
    item.name = 'test_example'
    item.own_markers = []

    mock_browser.return_value.is_open = True
    mock_driver = Mock()
    mock_browser.return_value.driver = mock_driver
    mock_generate_name.return_value = 'screenshot.png'
    mock_generate_path.return_value = '/path/to/screenshot.png'

    save_screenshot_on_failure(outcome, item)

    mock_generate_name.assert_called_once_with('setup_for_test_example')


@patch('surety.ui.pytest_addons.Browser')
def test_save_screenshot_not_called(mock_browser):
    outcome = Mock()
    report = Mock()
    report.failed = False
    outcome.get_result.return_value = report

    item = Mock()
    item.name = 'test_example'
    item.own_markers = []

    mock_browser.return_value.is_open = True
    mock_driver = Mock()
    mock_browser.return_value.driver = mock_driver

    save_screenshot_on_failure(outcome, item)

    mock_driver.save_screenshot.assert_not_called()


@patch('surety.ui.pytest_addons.Browser')
def test_save_screenshot_not_called_no_browser(mock_browser):
    outcome = Mock()
    report = Mock()
    report.failed = True
    report.when = 'call'
    outcome.get_result.return_value = report

    item = Mock()
    item.name = 'test_example'
    item.own_markers = []

    mock_browser.return_value.is_open = False
    mock_driver = Mock()
    mock_browser.return_value.driver = mock_driver

    save_screenshot_on_failure(outcome, item)

    mock_driver.save_screenshot.assert_not_called()


@patch('surety.ui.pytest_addons.Browser')
def test_save_screenshot_not_called_for_screenshot_test(mock_browser):
    outcome = Mock()
    report = Mock()
    report.failed = True
    report.when = 'call'
    outcome.get_result.return_value = report

    item = Mock()
    item.name = 'test_example'
    marker = Mock()
    marker.name = 'screenshot'
    item.own_markers = [marker]

    mock_browser.return_value.is_open = True
    mock_driver = Mock()
    mock_browser.return_value.driver = mock_driver

    save_screenshot_on_failure(outcome, item)

    mock_driver.save_screenshot.assert_not_called()


@patch('surety.ui.pytest_addons.Browser')
def test_save_screenshot_not_called_on_teardown_failure(mock_browser):
    outcome = Mock()
    report = Mock()
    report.failed = True
    report.when = 'teardown'
    outcome.get_result.return_value = report

    item = Mock()
    item.name = 'test_example'
    item.own_markers = []

    mock_browser.return_value.is_open = True
    mock_driver = Mock()
    mock_browser.return_value.driver = mock_driver

    save_screenshot_on_failure(outcome, item)

    mock_driver.save_screenshot.assert_not_called()


@patch('surety.ui.pytest_addons.Browser')
@patch('surety.ui.pytest_addons.folder.generate_file_name')
@patch('surety.ui.pytest_addons.folder.generate_file_path')
def test_screenshot_on_webdriver_exception(mock_generate_path,
                                           mock_generate_name, mock_browser):
    outcome = Mock()
    report = Mock()
    report.failed = True
    report.when = 'call'
    outcome.get_result.return_value = report

    item = Mock()
    item.name = 'test_example'
    item.own_markers = []

    mock_browser.return_value.is_open = True
    mock_driver = Mock()
    mock_driver.save_screenshot.side_effect = WebDriverException('Browser crashed')
    mock_browser.return_value.driver = mock_driver
    mock_generate_name.return_value = 'screenshot.png'
    mock_generate_path.return_value = '/path/to/screenshot.png'

    save_screenshot_on_failure(outcome, item)
