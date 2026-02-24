import pytest

from surety.ui.elements import Button, Checkbox

# pylint: disable=protected-access

def test_checkbox_state_changes(mock_web_element):
    checkbox = Checkbox(css='input[type="checkbox"]')
    checkbox._fixed_target = mock_web_element

    mock_web_element.is_selected.return_value = False
    assert checkbox.checked is False

    mock_web_element.is_selected.return_value = True
    assert checkbox.checked is True


def test_checked_is_true(mock_web_element):
    mock_web_element.is_selected.return_value = True

    checkbox = Checkbox(css='input[type=checkbox]')
    checkbox._fixed_target = mock_web_element

    assert checkbox.checked is True


def test_checked_is_false(mock_web_element):
    mock_web_element.is_selected.return_value = False

    checkbox = Checkbox(css='input[type=checkbox]')
    checkbox._fixed_target = mock_web_element

    assert checkbox.checked is False


def test_verify_checked_passes(mock_web_element):
    mock_web_element.is_selected.return_value = True

    checkbox = Checkbox(css='input[type=checkbox]')
    checkbox._fixed_target = mock_web_element

    checkbox.verify_checked(True)


def testverify_checked_fails(mock_web_element):
    mock_web_element.is_selected.return_value = False

    checkbox = Checkbox(css='input[type=checkbox]')
    checkbox._fixed_target = mock_web_element

    with pytest.raises(AssertionError, match='Expected checkbox to be'):
        checkbox.verify_checked(True)


def test_checkbox_inherits_from_button():
    checkbox = Checkbox(css='input[type=checkbox]')
    assert isinstance(checkbox, Button)
