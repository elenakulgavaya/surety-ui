import pytest
from unittest.mock import Mock, patch, MagicMock
from surety.ui.elements import Button


# conftest.py

@pytest.fixture
def mock_web_element():
    element = Mock()
    element.text = 'Click me'
    element.is_displayed.return_value = True
    element.get_attribute.return_value = None
    element.location = {'y': 0}
    element.size = {'height': 10, 'width': 100}
    element.location_once_scrolled_into_view = {'y': 0}
    return element


@pytest.fixture
def mock_driver(mock_web_element):
    driver = Mock()
    driver.find_element.return_value = mock_web_element
    driver.find_elements.return_value = [mock_web_element]
    driver.window_handles = ['window1']
    driver.get_window_size.return_value = {'height': 1050, 'width': 1680}
    driver.current_url = 'http://localhost/'
    return driver


@pytest.fixture(autouse=True)
def mock_browser(mock_driver):
    with patch('surety.ui.browser.Browser') as mock_b:
        with patch('surety.ui.elements.Browser') as mock_e:
            for mock in (mock_b, mock_e):
                instance = mock.return_value
                instance.driver = mock_driver
                instance.session = 0
                instance.recreate_session = Mock()

            yield mock_e  # yield the one elements.py uses
