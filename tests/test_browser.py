import pytest

from surety.ui.browser import Browser

# pylint: disable=protected-access

pytestmark = pytest.mark.usefixtures(
    'reset_browser',
    'mock_chrome_driver',
    'mock_chrome_class',
    'mock_cfg',
    'mock_folder'
)

def test_browser_is_singleton():
    browser1 = Browser()
    browser2 = Browser()

    assert browser1 is browser2


def test_driver_initialization(mock_chrome_driver, mock_chrome_class):
    browser = Browser()
    driver = browser.driver

    assert driver is mock_chrome_driver
    mock_chrome_class.assert_called_once()
    mock_chrome_driver.set_page_load_timeout.assert_called_with(15)
    mock_chrome_driver.set_window_size.assert_called_with(1680, 1050)



def test_driver_caching(mock_chrome_class):
    browser = Browser()
    driver1 = browser.driver
    driver2 = browser.driver

    assert driver1 is driver2
    mock_chrome_class.assert_called_once()



def test_browser_close():
    browser = Browser()
    saved_driver = browser.driver
    browser.close()

    saved_driver.quit.assert_called_once()
    assert browser._driver is None


def test_browser_close_when_not_open():
    browser = Browser()
    browser.close()

    assert browser._driver is None


def test_is_open_property_closed():
    browser = Browser()
    assert browser.is_open is False


def test_is_open_property_open():
    browser = Browser()
    _ = browser.driver

    assert browser.is_open is True


def test_is_open_property_after_close():
    browser = Browser()
    _ = browser.driver
    browser.close()

    assert browser.is_open is False


def test_session_property():
    browser = Browser()
    _ = browser.driver

    session1 = browser.session
    Browser.recreate_session()
    session2 = browser.session

    assert session2 == session1 + 1


def test_console_log_retrieval(mock_chrome_driver):
    mock_logs = [
        {'level': 'INFO', 'message': 'Info message'},
        {'level': 'SEVERE', 'message': 'Error message'},
        {'level': 'WARNING', 'message': 'Warning message'},
        {'level': 'SEVERE', 'message': 'Another error'},
    ]
    mock_chrome_driver.get_log.return_value = mock_logs

    browser = Browser()
    severe_logs = browser.console_log

    assert len(severe_logs) == 2
    assert all(log['level'] == 'SEVERE' for log in severe_logs)

    mock_chrome_driver.get_log.assert_called_with('browser')


def test_init_headless_mode(mock_cfg, mock_chrome_class):
    mock_cfg.Browser.headless = True

    browser = Browser()
    _ = browser.driver

    call_args = mock_chrome_class.call_args
    options = call_args[1]['options']

    assert '--headless=new' in options.arguments
    assert '--remote-debugging-pipe' in options.arguments


def test_init_devtools_option(mock_chrome_class, mock_cfg):
    mock_cfg.Browser.get.side_effect = lambda key: key == 'devtools' or None

    browser = Browser()
    _ = browser.driver

    call_args = mock_chrome_class.call_args
    options = call_args[1]['options']

    assert '--auto-open-devtools-for-tabs' in options.arguments


def test_init_no_sandbox_option(mock_chrome_class, mock_cfg):
    mock_cfg.Browser.get.side_effect = lambda key: key == 'no_sandbox' or None

    browser = Browser()
    _ = browser.driver

    call_args = mock_chrome_class.call_args
    options = call_args[1]['options']

    assert '--no-sandbox' in options.arguments
    assert '--disable-setuid-sandbox' in options.arguments
    assert '--disable-dev-shm-usage' in options.arguments
    assert '--disable-infobars' in options.arguments
    assert '--disable-browser-side-navigation' in options.arguments


def test_init_headless_experimental_options(mock_chrome_class,mock_cfg):
    mock_cfg.Browser.headless = True

    browser = Browser()
    _ = browser.driver

    call_args = mock_chrome_class.call_args
    options = call_args[1]['options']

    assert hasattr(options, '_experimental_options')
