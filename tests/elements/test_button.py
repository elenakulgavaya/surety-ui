from unittest.mock import Mock, patch

import pytest

from surety.ui.elements import Button

# pylint: disable=protected-access

def test_click_clears_target(mock_web_element):
    button = Button(css='button')
    button._fixed_target = mock_web_element

    with patch.object(button, 'scroll_to'):
        button.click()

    assert button._target is None


def test_text_property(mock_web_element):
    mock_web_element.text = 'Click Me'

    button = Button(css='.button')
    button._fixed_target = mock_web_element

    assert button.text == 'Click Me'


def test_button_click_once_loaded(mock_web_element, monkeypatch):
    button = Button(css='.button')
    button._fixed_target = mock_web_element

    mock_wait = Mock(return_value=True)
    monkeypatch.setattr('surety.ui.elements.wait', mock_wait)

    with patch.object(button, 'scroll_to'):
        result = button.click_once_loaded()

    assert result is True
    mock_wait.assert_called_once()


def test_click_and_switch_to_new_window(mock_web_element, mock_browser,
                                        monkeypatch):
    button = Button(css='.button')
    button._fixed_target = mock_web_element

    mock_driver = mock_browser.return_value.driver
    mock_driver.window_handles = ['window1']

    def side_effect_wait(func, **kwargs):
        mock_driver.window_handles = ['window1', 'window2']
        return True

    monkeypatch.setattr(
        'surety.ui.elements.wait', Mock(side_effect=side_effect_wait)
    )

    with patch.object(button, 'scroll_to'):
        button.click_and_switch_to_new_window()

    mock_driver.switch_to.window.assert_called_once_with('window2')


def test_button_is_disabled_returns_true(mock_web_element):
    mock_web_element.get_attribute.return_value = 'disabled'

    button = Button(css='.button')
    button._fixed_target = mock_web_element

    assert button.is_disabled is True


def test_button_is_disabled_returns_false(mock_web_element):
    mock_web_element.get_attribute.return_value = None

    button = Button(css='.button')
    button._fixed_target = mock_web_element

    assert button.is_disabled is False


def test_button_verify_text_passes(mock_web_element):
    mock_web_element.text = 'Submit'

    button = Button(css='.button')
    button._fixed_target = mock_web_element

    button.verify_text('Submit')


def test_button_verify_text_fails(mock_web_element):
    mock_web_element.text = 'Cancel'

    button = Button(css='.button')
    button._fixed_target = mock_web_element

    with pytest.raises(AssertionError, match='Unexpected menu text'):
        button.verify_text('Submit')


def test_button_wait_for_text(mock_web_element, monkeypatch):
    mock_web_element.text = 'Loading...'

    button = Button(css='.button')
    button._fixed_target = mock_web_element

    mock_wait = Mock()
    monkeypatch.setattr('surety.ui.elements.wait', mock_wait)

    button.wait_for_text('Done', timeout_seconds=5)

    mock_wait.assert_called_once()
    call_kwargs = mock_wait.call_args[1]
    assert call_kwargs['timeout_seconds'] == 5
    assert 'Done' in call_kwargs['waiting_for']
