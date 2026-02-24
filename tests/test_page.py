import pytest

from unittest.mock import MagicMock, Mock, patch

from selenium.webdriver import Keys

from surety.ui.browser import Browser, Page

# pylint: disable=duplicate-code
pytestmark = pytest.mark.usefixtures(
    'reset_browser',
    'mock_chrome_driver',
    'mock_chrome_class',
    'mock_cfg',
    'mock_folder'
)
# pylint: enable=duplicate-code

class TestPage(Page):
    base_url = 'https://example.com'
    url = 'test/page'


class FormatPage(Page):
    base_url = 'https://example.com'
    url = 'users/{}/profile'


def test_not_implemented_without_url():
    class NoUrlPage(Page):
        pass

    with pytest.raises(NotImplementedError, match='Page url is not specified'):
        NoUrlPage.open()


def test_open_with_url():
    browser = Browser()
    _ = browser.driver

    TestPage.open_page()

    browser.driver.get.assert_called_once_with('https://example.com/test/page')


def test_open_with_url_formatting():
    browser = Browser()
    _ = browser.driver

    FormatPage.open_page('123')

    browser.driver.get.assert_called_once_with('https://example.com/users/123/profile')


def test_open_with_url_postfix():
    browser = Browser()
    _ = browser.driver

    TestPage.open_page(url_postfix='?param=value')

    browser.driver.get.assert_called_once_with('https://example.com/test/page?param=value')


def test_open_calls_open_page():
    browser = Browser()
    _ = browser.driver

    TestPage.open('arg1', url_postfix='?test=1')

    browser.driver.get.assert_called_once_with('https://example.com/test/page?test=1')


def test_scroll_to_bottom(monkeypatch):
    monkeypatch.setattr('time.sleep', Mock())

    browser = Browser()
    _ = browser.driver

    Page.scroll_to_bottom()

    assert browser.driver.execute_script.call_count == 2
    browser.driver.execute_script.assert_any_call(
        "window.scrollTo(0,document.body.scrollHeight);"
    )
    browser.driver.execute_script.assert_any_call(
        "document.querySelector('#root').scrollTo(0,document.body.scrollHeight);"
    )


def test_get_current_url(mock_chrome_driver):
    mock_chrome_driver.current_url = 'https://example.com/current'

    browser = Browser()
    _ = browser.driver

    result = Page.get_current_url()

    assert result == 'https://example.com/current'


def test_wait_for_redirect(mock_chrome_driver, monkeypatch):
    mock_chrome_driver.current_url = 'https://example.com/?_=redirected'
    mock_wait = Mock()
    monkeypatch.setattr('surety.ui.browser.waiting.wait', mock_wait)

    browser = Browser()
    _ = browser.driver

    Page.wait_for_redirect()

    mock_wait.assert_called_once()


def test_open_with_only_base_url():
    class BaseUrlPage(Page):
        base_url = 'https://example.com'
        url = None

    browser = Browser()
    _ = browser.driver

    BaseUrlPage.open_page()

    browser.driver.get.assert_called_once_with('https://example.com/')


def test_open_recreates_session():
    browser = Browser()
    _ = browser.driver

    initial_session = browser.session
    TestPage.open_page()

    assert browser.session == initial_session + 1


def test_wait_for_current_url(mock_chrome_driver, monkeypatch):
    mock_chrome_driver.current_url = 'https://example.com/target'
    mock_wait = Mock()
    monkeypatch.setattr('surety.ui.browser.waiting.wait', mock_wait)

    browser = Browser()
    _ = browser.driver

    Page.wait_for_current_url('https://example.com/target')

    mock_wait.assert_called_once()
    call_kwargs = mock_wait.call_args[1]
    assert call_kwargs['timeout_seconds'] == 1
    assert call_kwargs['waiting_for'] == 'url to update'


def test_is_open_returns_true(mock_chrome_driver):
    mock_chrome_driver.current_url = 'https://example.com/test/page'

    browser = Browser()
    _ = browser.driver

    assert TestPage.is_open()


def test_is_open_returns_false(mock_chrome_driver):
    mock_chrome_driver.current_url = 'https://example.com/other/page'

    browser = Browser()
    _ = browser.driver

    assert TestPage.is_open() is False


def test_is_open_skip_params(mock_chrome_driver):
    mock_chrome_driver.current_url = 'https://example.com/test/page?param=value'

    browser = Browser()
    _ = browser.driver

    assert TestPage.is_open(skip_params=True)


def test_is_open_with_params(mock_chrome_driver):
    mock_chrome_driver.current_url = 'https://example.com/test/page?param=value'

    browser = Browser()
    _ = browser.driver

    assert TestPage.is_open(skip_params=False) is False


def test_is_open_url_postfix(mock_chrome_driver):
    mock_chrome_driver.current_url = 'https://example.com/test/page/extra'

    browser = Browser()
    _ = browser.driver

    assert TestPage.is_open(url_postfix='/extra')


def test_is_open_formatting(mock_chrome_driver):
    mock_chrome_driver.current_url = 'https://example.com/users/123/profile'

    browser = Browser()
    _ = browser.driver

    assert FormatPage.is_open('123')


def test_verify_current_url_pass(mock_chrome_driver):
    mock_chrome_driver.current_url = 'https://example.com/test/page'

    browser = Browser()
    _ = browser.driver

    TestPage.verify_current_url()


def test_verify_current_url_fails(mock_chrome_driver):
    mock_chrome_driver.current_url = 'https://example.com/wrong/page'

    browser = Browser()
    _ = browser.driver

    with pytest.raises(AssertionError, match='Unexpected url'):
        TestPage.verify_current_url()


def test_verify_current_url_skip_params(mock_chrome_driver):
    mock_chrome_driver.current_url = 'https://example.com/test/page?param=value'

    browser = Browser()
    _ = browser.driver

    TestPage.verify_current_url(skip_params=True)


def test_verify_current_url_with_postfix(mock_chrome_driver):
    mock_chrome_driver.current_url = 'https://example.com/test/page/extra'

    browser = Browser()
    _ = browser.driver

    TestPage.verify_current_url(url_postfix='/extra')


def test_go_back():
    browser = Browser()
    _ = browser.driver

    Page.go_back()

    browser.driver.back.assert_called_once()


def test_press_key(mock_chrome_driver):
    mock_ac = MagicMock()
    with patch('surety.ui.browser.action_chains.ActionChains',
               return_value=mock_ac) as MockAC:
        Page.press_key(Keys.ENTER)
        MockAC.assert_called_once_with(mock_chrome_driver)
        mock_ac.send_keys.assert_called_once_with(Keys.ENTER)
        mock_ac.send_keys.return_value.perform.assert_called_once()


def test_retry_on_js_reload_succeeds_first_try(monkeypatch):
    from surety.ui.browser import retry_on_js_reload

    mock_function = Mock(return_value='success')
    mock_refresh = Mock()
    mock_wait = Mock()
    monkeypatch.setattr('surety.ui.browser.wait', mock_wait)

    result = retry_on_js_reload(mock_function, mock_refresh, timeout_seconds=2)

    assert result == 'success'
    mock_function.assert_called_once()
    mock_refresh.assert_not_called()


def test_retry_on_js_reload_handles_stale_element_exception(monkeypatch):
    from surety.ui.browser import retry_on_js_reload
    from selenium.common.exceptions import StaleElementReferenceException

    mock_function = Mock(side_effect=[
        StaleElementReferenceException('Element is stale'),
        'success'
    ])
    mock_refresh = Mock()
    mock_wait = Mock(side_effect=lambda action, **kwargs: action())
    monkeypatch.setattr('surety.ui.browser.wait', mock_wait)

    result = retry_on_js_reload(mock_function, mock_refresh, timeout_seconds=2)

    assert result == 'success'
    assert mock_function.call_count == 2
    mock_refresh.assert_called_once()


def test_retry_on_js_reload_handles_element_click_intercepted(monkeypatch):
    from surety.ui.browser import retry_on_js_reload
    from selenium.common.exceptions import ElementClickInterceptedException

    mock_function = Mock(side_effect=[
        ElementClickInterceptedException('Click intercepted'),
        'success'
    ])
    mock_refresh = Mock()
    mock_wait = Mock(side_effect=lambda action, **kwargs: action())
    monkeypatch.setattr('surety.ui.browser.wait', mock_wait)

    result = retry_on_js_reload(mock_function, mock_refresh, timeout_seconds=2)

    assert result == 'success'
    assert mock_function.call_count == 2
    mock_refresh.assert_called_once()


def test_wait_for_window_closed(mock_chrome_driver):
    mock_chrome_driver.window_handles = ['handle1']
    with patch('surety.ui.browser.wait') as mock_wait:
        Page.wait_for_window_closed(timeout=3)
        mock_wait.assert_called_once()
        assert mock_wait.call_args[1]['timeout_seconds'] == 3
        assert mock_wait.call_args[1]['waiting_for'] == 'extra windows to close'


def test_wait_for_window_closed_lambda_one_handle(mock_chrome_driver):
    mock_chrome_driver.window_handles = ['only_one']
    assert (lambda: len(mock_chrome_driver.window_handles) == 1)() is True


def test_wait_for_window_closed_lambda_multiple_handles(mock_chrome_driver):
    mock_chrome_driver.window_handles = ['h1', 'h2']
    assert (lambda: len(mock_chrome_driver.window_handles) == 1)() is False


def test_switch_to_default_window(mock_chrome_driver):
    mock_chrome_driver.window_handles = ['main_handle', 'popup_handle']
    Page.switch_to_default_window()
    mock_chrome_driver.switch_to.window.assert_called_once_with('main_handle')
