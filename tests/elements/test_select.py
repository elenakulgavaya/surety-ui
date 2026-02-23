import pytest
from unittest.mock import MagicMock, Mock, patch, PropertyMock
from selenium.common.exceptions import StaleElementReferenceException

from surety.ui.elements import (
    Button, Link, TextInput, Label, Select, Checkbox, Container, Table, TableRow
)
from surety.ui.browser import Element, Elements, retry_on_js_reload


def test_select_located_property(mock_web_element, monkeypatch):
    mock_base_select = Mock()
    mock_select_class = Mock(return_value=mock_base_select)
    monkeypatch.setattr('surety.ui.elements.BaseSelect', mock_select_class)

    select = Select(css='select')
    select._fixed_target = mock_web_element

    result = select.located

    mock_select_class.assert_called_once_with(mock_web_element)
    assert result == mock_base_select


def test_select_wait_for_value(mock_web_element, monkeypatch):
    mock_base_select = Mock()
    mock_base_select.options = ['option1', 'option2']
    type(mock_base_select).options = PropertyMock(side_effect=[
        [],
        ['option1', 'option2']
    ])
    monkeypatch.setattr('surety.ui.elements.BaseSelect', Mock(return_value=mock_base_select))


    select = Select(css='select')
    select._fixed_target = mock_web_element

    select.wait_for_value()


def test_select_by_value(mock_web_element, monkeypatch):
    mock_base_select = Mock()
    monkeypatch.setattr('surety.ui.elements.BaseSelect', Mock(return_value=mock_base_select))

    select = Select(css='select')
    select._fixed_target = mock_web_element

    select.select(value='option1')

    mock_base_select.select_by_value.assert_called_once_with('option1')


def test_select_by_index(mock_web_element, monkeypatch):
    mock_base_select = Mock()
    monkeypatch.setattr('surety.ui.elements.BaseSelect', Mock(return_value=mock_base_select))

    select = Select(css='select')
    select._fixed_target = mock_web_element

    select.select(index=2)

    mock_base_select.select_by_index.assert_called_once_with(2)


def test_select_by_text(mock_web_element, monkeypatch):
    mock_base_select = Mock()
    monkeypatch.setattr('surety.ui.elements.BaseSelect', Mock(return_value=mock_base_select))

    select = Select(css='select')
    select._fixed_target = mock_web_element

    select.select(text='Option Text')

    mock_base_select.select_by_visible_text.assert_called_once_with('Option Text')


def test_select_requires_parameters(mock_web_element, monkeypatch):
    mock_base_select = Mock()
    monkeypatch.setattr('surety.ui.elements.BaseSelect', Mock(return_value=mock_base_select))

    select = Select(css='select')
    select._fixed_target = mock_web_element

    with pytest.raises(ValueError, match='provide value for select'):
        select.select()


def test_select_all_options_property(mock_web_element, monkeypatch):
    mock_option1 = Mock()
    mock_option1.text = 'Option 1'
    mock_option2 = Mock()
    mock_option2.text = 'Option 2'

    mock_base_select = Mock()
    mock_base_select.options = [mock_option1, mock_option2]
    monkeypatch.setattr(
        'surety.ui.elements.BaseSelect',
        Mock(return_value=mock_base_select)
    )

    select = Select(css='select')
    select._fixed_target = mock_web_element

    assert select.all_options == ['Option 1', 'Option 2']


def test_select_all_options_order(mock_web_element, monkeypatch):
    mock_opts = [MagicMock(text=f'Option {i}') for i in range(3)]
    mock_base_select = MagicMock()
    mock_base_select.options = mock_opts
    monkeypatch.setattr(
        'surety.ui.elements.BaseSelect',
        Mock(return_value=mock_base_select)
    )

    select = Select(name='select')
    select._fixed_target = mock_web_element

    assert select.all_options == ['Option 0', 'Option 1', 'Option 2']


def test_select_empty_options(mock_web_element, monkeypatch):
    mock_base_select = MagicMock()
    mock_base_select.options = []
    monkeypatch.setattr(
        'surety.ui.elements.BaseSelect',
        Mock(return_value=mock_base_select)
    )

    select = Select(name='select')
    select._fixed_target = mock_web_element

    assert select.all_options == []


def test_select_selected_option_property(mock_web_element, monkeypatch):
    mock_selected = Mock()
    mock_selected.text = 'Selected Option'

    mock_base_select = Mock()
    mock_base_select.first_selected_option = mock_selected
    monkeypatch.setattr(
        'surety.ui.elements.BaseSelect',
        Mock(return_value=mock_base_select)
    )

    select = Select(css='select')
    select._fixed_target = mock_web_element

    assert select.selected_option == 'Selected Option'


def test_select_verify_selected_option_passes(mock_web_element, monkeypatch):
    mock_selected = Mock()
    mock_selected.text = 'Option 1'

    mock_base_select = Mock()
    mock_base_select.first_selected_option = mock_selected
    monkeypatch.setattr(
        'surety.ui.elements.BaseSelect',
        Mock(return_value=mock_base_select)
    )

    select = Select(css='select')
    select._fixed_target = mock_web_element

    select.verify_selected_option('Option 1')


def test_select_verify_selected_option_fails(mock_web_element, monkeypatch):
    mock_selected = Mock()
    mock_selected.text = 'Option 1'

    mock_base_select = Mock()
    mock_base_select.first_selected_option = mock_selected
    monkeypatch.setattr('surety.ui.elements.BaseSelect', Mock(return_value=mock_base_select))

    select = Select(css='select')
    select._fixed_target = mock_web_element

    with pytest.raises(AssertionError, match='Unexpected selected option'):
        select.verify_selected_option('Option 2')
