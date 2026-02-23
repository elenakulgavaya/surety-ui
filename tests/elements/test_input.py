import pytest

from unittest.mock import Mock, patch

from surety.ui.elements import TextInput


def test_input_with_clear(mock_web_element):
    text_input = TextInput(name='input')
    text_input._fixed_target = mock_web_element

    with patch.object(text_input, 'wait_for_load'):
        text_input.input('test value')

    mock_web_element.click.assert_called_once()
    mock_web_element.clear.assert_called_once()
    mock_web_element.send_keys.assert_called_with('test value')


def test_input_empty_string(mock_web_element):
    text_input = TextInput(name='input')
    text_input._fixed_target = mock_web_element

    with patch.object(text_input, 'wait_for_load'):
        text_input.input('')

    mock_web_element.send_keys.assert_called_with('')


def test_input_long_text(mock_web_element):
    text_input = TextInput(name='input')
    text_input._fixed_target = mock_web_element
    long_text = 'test_value' * 100

    with patch.object(text_input, 'wait_for_load'):
        text_input.input(long_text)

    mock_web_element.send_keys.assert_called_with(long_text)


def test_text_input_safe_input_method(mock_web_element, monkeypatch):
    mock_action_chains = Mock()
    mock_chains_instance = Mock()
    mock_action_chains.return_value = mock_chains_instance
    monkeypatch.setattr('surety.ui.elements.ActionChains', mock_action_chains)

    text_input = TextInput(css='input')
    text_input._fixed_target = mock_web_element

    with patch.object(text_input, 'wait_for_load'):
        text_input.safe_input('test value')

    mock_web_element.click.assert_called_once()
    mock_chains_instance.send_keys.assert_called_once_with('test value')
    mock_chains_instance.perform.assert_called_once()


def test_text_input_clear_and_type(mock_web_element):
    text_input = TextInput(css='input')
    text_input._fixed_target = mock_web_element
    text_input.safe_input = Mock()

    with patch.object(text_input, 'wait_for_load'):
        text_input.clear_and_type('new value')

    mock_web_element.clear.assert_called_once()
    text_input.safe_input.assert_called_once_with('new value')


def test_text_input_get_value(mock_web_element):
    mock_web_element.get_attribute.return_value = 'input value'

    text_input = TextInput(css='input')
    text_input._fixed_target = mock_web_element

    with patch.object(text_input, 'wait_for_load'):
        result = text_input.get_value()

    mock_web_element.get_attribute.assert_called_once_with('value')
    assert result == 'input value'


def test_text_input_set_value(mock_web_element, mock_browser):
    mock_driver = mock_browser.return_value.driver

    text_input = TextInput(css='input')
    text_input._fixed_target = mock_web_element

    with patch.object(text_input, 'wait_for_load'):
        text_input.set_value('javascript value')

    mock_driver.execute_script.assert_called_once_with(
        'arguments[0].value = arguments[1]',
        mock_web_element,
        'javascript value'
    )


def test_text_input_verify_value_passes(mock_web_element):
    mock_web_element.get_attribute.return_value = '123'

    text_input = TextInput(css='input')
    text_input._fixed_target = mock_web_element

    with patch.object(text_input, 'wait_for_load'):
        text_input.verify_value(123)


def test_text_input_verify_value_fails(mock_web_element):
    mock_web_element.get_attribute.return_value = '123'

    text_input = TextInput(css='input')
    text_input._fixed_target = mock_web_element

    with patch.object(text_input, 'wait_for_load'):
        with pytest.raises(AssertionError, match='Unexpected input value'):
            text_input.verify_value(456)
