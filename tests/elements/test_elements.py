from unittest.mock import MagicMock, patch, Mock

from selenium.common import StaleElementReferenceException, WebDriverException
from waiting import TimeoutExpired

from surety.ui.browser import Element, Elements, retry_on_js_reload

# pylint: disable=protected-access

def test_elements_initialization_with_element_class():
    mock_element_class = MagicMock()
    elems = Elements(css='button.item', element_class=mock_element_class)

    assert elems.element_class is mock_element_class


def test_elements_initialization_without_element_class():
    elems = Elements(xpath='//div[@class="item"]')

    assert elems.element_class is None


def test_elements_inherits_from_element():
    assert issubclass(Elements, Element)


def test_retry_success_first_attempt():
    mock_func = Mock(return_value='result')
    mock_refresh = Mock()

    result = retry_on_js_reload(mock_func, mock_refresh, timeout_seconds=1)

    assert result == 'result'
    mock_func.assert_called()


def test_retry_on_stale_element(monkeypatch):
    call_count = 0
    results = [StaleElementReferenceException(), 'success']

    def mock_func():
        nonlocal call_count
        val = results[call_count]
        call_count += 1
        if isinstance(val, Exception):
            raise val
        return val

    mock_refresh = Mock()

    def wait_impl(action, **_):
        # run until action returns truthy
        for _ in range(5):
            result = action()
            if result:
                return result

        return None

    monkeypatch.setattr('surety.ui.browser.waiting.wait', wait_impl)

    result = retry_on_js_reload(mock_func, mock_refresh)

    assert result == 'success'
    mock_refresh.assert_called_once()


def test_elements_reload_with_parent(mock_web_element):
    mock_parent = MagicMock()
    mock_parent.find_elements = Mock(return_value=[mock_web_element])

    els = Elements(css='div')
    els._parent = mock_parent
    els.reload(parent=MagicMock())

    mock_parent.invalidate.assert_called_once()
    assert els._target == [mock_web_element]


def test_elements_reload_with_element_class(mock_web_element):
    mock_parent_arg = MagicMock()
    mock_parent_arg.find_elements = Mock(return_value=[mock_web_element])

    els = Elements(css='div', element_class=Element)
    els._parent = None
    els.reload(parent=mock_parent_arg)

    assert len(els._target) == 1
    assert isinstance(els._target[0], Element)


def test_elements_is_present(mock_web_element):
    els = Elements(css='div')
    els._fixed_target = [mock_web_element]
    assert els.is_present(timeout=1)


def test_elements_is_present_false_on_exception(mock_web_element):
    els = Elements(css='div')
    els._fixed_target = [mock_web_element]
    with patch('surety.ui.browser.wait', Mock(side_effect=WebDriverException())):
        assert els.is_present(timeout=0) is False


def test_elements_is_present_false_on_timeout(mock_web_element):
    els = Elements(css='div')
    els._fixed_target = [mock_web_element]
    with patch('surety.ui.browser.wait',
               Mock(side_effect=TimeoutExpired('', 0))):
        assert els.is_present(timeout=0) is False


def test_elements_is_present_false_on_index_error():
    els = Elements(css='div')
    els._fixed_target = []
    with patch('surety.ui.browser.wait', Mock(side_effect=IndexError())):
        assert els.is_present(timeout=0) is False


def test_elements_get_by_attribute_not_found(mock_web_element):
    mock_web_element.get_attribute = Mock(return_value='nope')
    els = Elements(css='div', element_class=Element)
    els._fixed_target = [mock_web_element]
    assert els.get_by_attribute(data_id='missing') is None



def test_elements_get_by_text_with_strip(mock_web_element):
    mock_web_element.text = '  hello  '
    els = Elements(css='div')
    els._fixed_target = [mock_web_element]

    assert els.get_by_text('hello', strip=True) is mock_web_element


def test_elements_get_by_attribute(mock_web_element):
    mock_web_element.get_attribute.return_value = 'test'
    els = Elements(css='div')
    els._fixed_target = [mock_web_element]

    assert els.get_by_attribute(attribute='test') is mock_web_element


def test_elements_get_by_text_not_found(mock_web_element):
    mock_web_element.text = 'something'
    els = Elements(css='div')
    els._fixed_target = [mock_web_element]
    assert els.get_by_text('missing') is None


def test_elements_click_by_text(mock_web_element):
    mock_web_element.text = 'Click me'
    els = Elements(css='div')
    els._fixed_target = [mock_web_element]
    els.click_by_text('Click me')

    mock_web_element.click.assert_called_once()


def test_elements_wait_for_items_load_nonzero(mock_driver, mock_web_element):
    els = Elements(css='div')
    els._fixed_target = [mock_web_element]
    els.wait_for_items_load(items_count=1)

    mock_driver.implicitly_wait.assert_called_with(1)


def test_elements_wait_for_some_items(mock_web_element):
    els = Elements(css='div')
    els._fixed_target = [mock_web_element]
    els.wait_for_some_items(timeout_seconds=3)


def test_elements_get_not_empty_labels(mock_web_element):
    el2 = MagicMock()
    el2.text = ''
    mock_web_element.text = 'Label A'

    els = Elements(css='div')
    els._fixed_target = [mock_web_element, el2]

    assert els.get_not_empty_labels() == ['Label A']


def test_elements_wait_for_labels(mock_web_element):
    mock_web_element.text = 'A'

    els = Elements(css='div')
    els._fixed_target = [mock_web_element]
    els.wait_for_labels(count=1, timeout_seconds=3)


def test_elements_verify_labels(mock_web_element):
    mock_web_element.text = 'X'
    els = Elements(css='div')
    els._fixed_target = [mock_web_element]

    els.verify_labels(['X'])

def test_elements_len(mock_web_element):
    els = Elements(css='div')
    els._fixed_target = [mock_web_element]
    assert len(els) == 1

def test_elements_getitem(mock_web_element):
    els = Elements(css='div')
    els._fixed_target = [mock_web_element]
    assert els[0] is mock_web_element

def test_elements_iter(mock_web_element):
    els = Elements(css='div')
    els._fixed_target = [mock_web_element]
    assert list(els) == [mock_web_element]
