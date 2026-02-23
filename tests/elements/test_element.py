from unittest.mock import MagicMock, patch, Mock

from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from waiting import TimeoutExpired

from surety.ui.browser import Element


def test_element_initialization_with_css():
    elem = Element(css='button.primary')
    assert elem.by == By.CSS_SELECTOR
    assert elem.by_value == 'button.primary'

def test_element_initialization_with_xpath():
    elem = Element(xpath='//button[@id="submit"]')
    assert elem.by == By.XPATH
    assert elem.by_value == '//button[@id="submit"]'


def test_element_initialization_with_name():
    elem = Element(name='username')
    assert elem.by == By.NAME
    assert elem.by_value == 'username'


def test_element_default_by_id():
    elem = Element('myid')
    assert elem.by == By.ID
    assert elem.by_value == 'myid'


def test_element_explicit_by_parameter():
    elem = Element(by_value='my-value', by=By.CLASS_NAME)
    assert elem.by == By.CLASS_NAME
    assert elem.by_value == 'my-value'


def test_element_invalidate():
    elem = Element(css='span')
    elem._target = MagicMock()

    elem.invalidate()

    assert elem._target is None


def test_element_get_attribute():
    mock_web_element = MagicMock()
    mock_web_element.get_attribute.return_value = 'button'
    elem = Element.set_located(mock_web_element)

    result = elem.get_attribute('type')

    assert result == 'button'
    mock_web_element.get_attribute.assert_called_with(name='type')


def test_element_text_property():
    mock_web_element = MagicMock()
    mock_web_element.text = 'Button Text'
    elem = Element.set_located(mock_web_element)

    assert elem.text == 'Button Text'


def test_element_check_browser_session_different(monkeypatch):
    mock_browser = MagicMock()
    mock_browser.session = 2
    monkeypatch.setattr('surety.ui.browser.Browser', lambda: mock_browser)

    elem = Element(css='span')
    elem._browser_session = 1
    elem._target = MagicMock()

    elem.check_browser_session()

    assert elem._target is None


@patch('surety.ui.browser.wait')
def test_element_wait_for_load(mock_wait):
    mock_wait.return_value = True
    elem = Element(css='div')

    elem.wait_for_load(timeout_seconds=3)

    mock_wait.assert_called_once()


@patch('surety.ui.browser.wait')
def test_element_wait_for_not_present(mock_wait):
    mock_wait.return_value = True
    elem = Element(css='div')

    elem.wait_for_not_present(timeout_seconds=2)

    mock_wait.assert_called_once()


@patch('surety.ui.browser.wait')
@patch('surety.ui.browser.Browser')
def test_element_scroll_to(mock_browser, mock_wait, monkeypatch):
    mock_driver = MagicMock()
    mock_driver.get_window_size.return_value = {'height': 1000}
    mock_browser.return_value.driver = mock_driver

    mock_web_elem = MagicMock()
    mock_web_elem.size = {'height': 100}
    mock_web_elem.location = {'y': 50}

    elem = Element.set_located(mock_web_elem)

    with patch.object(elem, 'wait_for_load'):
        elem.scroll_to()


def test_element_invalidate_cascade():
    parent = Element(css='div')
    child = Element(css='span')
    child.parent = parent

    parent._target = MagicMock()
    child._target = MagicMock()

    child.invalidate()

    assert child._target is None
    assert parent._target is None


def test_element_invalidate_without_parent():
    elem = Element(css='div')
    elem._target = MagicMock()

    elem.invalidate()

    assert elem._target is None


def test_element_get_multiple_attributes():
    mock_web = MagicMock()
    mock_web.get_attribute.side_effect = lambda name: {
        'class': 'button-primary',
        'id': 'submit-btn',
        'disabled': None
    }.get(name)

    elem = Element.set_located(mock_web)

    assert elem.get_attribute('class') == 'button-primary'
    assert elem.get_attribute('id') == 'submit-btn'
    assert elem.get_attribute('disabled') is None


def test_element_is_list_item_container_true(mock_web_element):
    el = Element(css='div')
    el._fixed_target = mock_web_element
    assert el.is_list_item_container() is True


def test_element_is_list_item_container_false():
    el = Element(css='div')
    el._fixed_target = None
    assert el.is_list_item_container() is False


def test_element_invalidate_clears_target(mock_web_element):
    el = Element(css='div')
    el._target = mock_web_element
    el._parent = None
    el.invalidate()
    assert el._target is None


def test_element_invalidate_calls_parent_invalidate(mock_web_element):
    el = Element(css='div')
    el._target = mock_web_element
    mock_parent = MagicMock()
    el._parent = mock_parent
    el.invalidate()
    mock_parent.invalidate.assert_called_once()


def test_element_find_element(mock_web_element):
    el = Element(css='div')
    el._fixed_target = mock_web_element
    el.find_element(By.CSS_SELECTOR, '.child')
    mock_web_element.find_element.assert_called_once_with(by=By.CSS_SELECTOR, value='.child')


def test_element_find_elements(mock_web_element):
    el = Element(css='div')
    el._fixed_target = mock_web_element
    el.find_elements(By.CSS_SELECTOR, '.children')
    mock_web_element.find_elements.assert_called_once_with(by=By.CSS_SELECTOR, value='.children')


def test_element_located_finds_by_driver(mock_driver, mock_web_element):
    mock_driver.find_element = Mock(return_value=mock_web_element)
    el = Element(css='div.test')
    assert el.located is mock_web_element


def test_element_descriptor_sets_parent(mock_web_element):
    class Container(Element):
        child = Element(css='.child')

    container = Container(css='.container')
    container._fixed_target = mock_web_element

    descriptor = Container.__dict__['child']
    result = descriptor.__get__(container, Container)
    assert result is descriptor
    assert descriptor._parent is container


def test_element_getattr_delegates_to_located(mock_web_element):
    mock_web_element.some_custom_attr = 'hello'
    el = Element(css='div')
    el._fixed_target = mock_web_element
    assert el.some_custom_attr == 'hello'


def test_element_is_not_present_true(mock_web_element):
    el = Element(css='div')
    el._fixed_target = mock_web_element
    with patch('surety.ui.browser.wait', Mock()):
        assert el.is_not_present(timeout_seconds=1) is True


def test_element_is_not_present_returns_false_on_timeout(mock_web_element):
    el = Element(css='div')
    el._fixed_target = mock_web_element
    with patch('surety.ui.browser.wait',
               Mock(side_effect=TimeoutExpired('', 1))):
        assert el.is_not_present(timeout_seconds=1) is False



def test_element_is_present_false_on_exception(mock_web_element):
    el = Element(css='div')
    el._fixed_target = mock_web_element
    with patch('surety.ui.browser.wait', Mock(side_effect=WebDriverException())):
        assert el.is_present(timeout=1) is False


def test_element_is_present_false_on_timeout(mock_web_element):
    el = Element(css='div')
    el._fixed_target = mock_web_element
    with patch('surety.ui.browser.wait',
               Mock(side_effect=TimeoutExpired('', 1))):
        assert el.is_present(timeout=1) is False


def test_scroll_when_below_viewport(mock_driver, mock_web_element):
    mock_web_element.location = {'y': 1100}
    mock_web_element.size = {'height': 50}
    mock_web_element.location_once_scrolled_into_view = {'y': 900}
    mock_driver.get_window_size.return_value = {'height': 1050}

    el = Element(css='div')
    el._fixed_target = mock_web_element

    with patch('surety.ui.browser.wait') as mock_wait:
        el.scroll_to(timeout=1)

    assert mock_wait.call_count == 2  # wait_for_load + scroll wait


def test_element_save_screenshot(mock_web_element):
    el = Element(css='div')
    el._fixed_target = mock_web_element
    el.save_screenshot('shot.png')
    mock_web_element.screenshot.assert_called_once_with(filename='shot.png')


def test_element_get_screenshot_as_png(mock_web_element):
    mock_web_element.screenshot_as_png = b'\x89PNG'
    el = Element(css='div')
    el._fixed_target = mock_web_element
    assert el.get_screenshot_as_png() == b'\x89PNG'


def test_element_delete(mock_driver, mock_web_element):
    el = Element(css='div')
    el._fixed_target = mock_web_element

    with patch('surety.ui.browser.wait', Mock()):
        el.delete()

    mock_driver.execute_script.assert_called_once_with(
        'arguments[0].parentNode.removeChild(arguments[0])',
        mock_web_element
    )


def test_element_wait_for_size(mock_web_element):
    mock_web_element.size = {'height': 100, 'width': 200}
    el = Element(css='div')
    el._fixed_target = mock_web_element

    with patch('surety.ui.browser.wait') as mock_wait:
        el.wait_for_size(height=100, width=200)

    mock_wait.assert_called_once()


def test_wait_for_size_height_mismatch(mock_web_element):
    mock_web_element.size = {'height': 50, 'width': 200}
    el = Element(css='div')
    el._fixed_target = mock_web_element

    results = []

    def fake_wait(fn, **kwargs):
        results.append(fn())  # call is_of_size directly

    with patch('surety.ui.browser.wait', fake_wait):
        el.wait_for_size(height=100, width=None)

    assert results[0] is False


def test_wait_for_size_width_mismatch(mock_web_element):
    mock_web_element.size = {'height': 100, 'width': 50}
    el = Element(css='div')
    el._fixed_target = mock_web_element

    results = []

    def fake_wait(fn, **kwargs):
        results.append(fn())

    with patch('surety.ui.browser.wait', fake_wait):
        el.wait_for_size(height=None, width=200)

    assert results[0] is False


def test_wait_for_size_both_match_returns_true(mock_web_element):
    mock_web_element.size = {'height': 100, 'width': 200}
    el = Element(css='div')
    el._fixed_target = mock_web_element

    results = []

    def fake_wait(fn, **kwargs):
        results.append(fn())

    with patch('surety.ui.browser.wait', fake_wait):
        el.wait_for_size(height=100, width=200)

    assert results[0] is True


def test_verify_displayed_with_screenshot(mock_web_element):
    mock_web_element.size = {'height': 100, 'width': 200}
    mock_web_element.location = {'y': 10}
    el = Element(css='div')
    el._fixed_target = mock_web_element

    with patch('surety.ui.browser.Cfg') as mock_cfg:
        with patch('surety.ui.browser.PageScreenshot') as mock_ps:
            mock_cfg.Screenshot.compare = True
            el.verify_displayed(height=100, width=200)

    mock_ps.compare.assert_called_once_with(el)


def test_verify_displayed_without_screenshot(mock_web_element):
    mock_web_element.size = {'height': 100, 'width': 200}
    mock_web_element.location = {'y': 10}
    mock_web_element.is_displayed.return_value = True
    el = Element(css='div')
    el._fixed_target = mock_web_element

    with patch('surety.ui.browser.Cfg') as mock_cfg:
        mock_cfg.Screenshot.compare = False
        el.verify_displayed(height=100, width=200)

    mock_web_element.is_displayed.assert_called()


def test_element_hover(mock_driver, mock_web_element):
    el = Element(css='div')
    el._fixed_target = mock_web_element

    mock_ac = MagicMock()
    with patch('surety.ui.browser.ActionChains', return_value=mock_ac) as MockAC:
        result = el.hover()

    assert result is True
    MockAC.assert_called_once_with(mock_driver)
    mock_ac.move_to_element.assert_called_once_with(mock_web_element)
