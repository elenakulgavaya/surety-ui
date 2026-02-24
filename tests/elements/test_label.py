from unittest.mock import Mock, patch, PropertyMock

import pytest

from selenium.common.exceptions import StaleElementReferenceException

from surety.ui.elements import Label

# pylint: disable=protected-access

def test_label_text_property(mock_web_element):
    mock_web_element.text = 'Label Text'

    label = Label(css='.label')
    label._fixed_target = mock_web_element

    assert label.text == 'Label Text'


def test_label_is_displayed_property(mock_web_element):
    mock_web_element.is_displayed = True

    label = Label(css='.label')
    label._fixed_target = mock_web_element

    assert label.is_displayed is True


def test_label_text_conversion_to_string(mock_web_element):
    mock_web_element.text = 'Status: 123'

    label = Label(css='label')
    label._fixed_target = mock_web_element

    with patch.object(label, 'wait_for_load'):
        label.verify_text('Status: 123')


def test_label_wait_for_text_match(mock_web_element, monkeypatch):
    mock_web_element.text = 'Expected'

    label = Label(css='label')
    label._fixed_target = mock_web_element

    mock_wait = Mock()
    monkeypatch.setattr('surety.ui.elements.wait', mock_wait)

    label.wait_for_text('Expected')

    mock_wait.assert_called_once()


def test_label_wait_for_updated(mock_web_element, monkeypatch):
    type(mock_web_element).text = PropertyMock(side_effect=[
        'initial',
        'new'
    ])

    label = Label(css='.label')
    label._fixed_target = mock_web_element

    label.wait_for_updated(timeout=2)



def test_label_wait_for_text(mock_web_element, monkeypatch):
    mock_web_element.text = 'expected'

    label = Label(css='.label')
    label._fixed_target = mock_web_element

    mock_wait = Mock()
    monkeypatch.setattr('surety.ui.elements.wait', mock_wait)

    label.wait_for_text('expected', timeout=3)

    mock_wait.assert_called_once()
    call_kwargs = mock_wait.call_args[1]
    assert call_kwargs['timeout_seconds'] == 3
    assert 'expected' in call_kwargs['waiting_for']


def test_wait_for_text_handles_stale_exception(mock_web_element, monkeypatch):
    type(mock_web_element).text = PropertyMock(side_effect=[
        StaleElementReferenceException('Stale'),
        'expected'
    ])

    label = Label(css='.label')
    label._fixed_target = mock_web_element
    label.invalidate = Mock()

    def wait_impl(func, **kwargs):
        func()  # raises StaleElementReferenceException -> calls invalidate()
        func()  # returns True

    monkeypatch.setattr('surety.ui.elements.wait', wait_impl)

    with patch.object(label, 'wait_for_load'):
        label.wait_for_text('expected', timeout=2)

    label.invalidate.assert_called_once()


def test_label_verify_text_passes(mock_web_element):
    mock_web_element.text = '123'

    label = Label(css='.label')
    label._fixed_target = mock_web_element

    with patch.object(label, 'wait_for_load'):
        label.verify_text(123)


def test_label_verify_text_fails(mock_web_element):
    mock_web_element.text = 'wrong'

    label = Label(css='.label')
    label._fixed_target = mock_web_element

    with patch.object(label, 'wait_for_load'):
        with pytest.raises(AssertionError, match='Unexpected label text'):
            label.verify_text('expected')
