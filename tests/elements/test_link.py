from surety.ui.elements import Button, Link


def test_link_url_property(mock_web_element):
    mock_web_element.get_attribute.return_value = 'https://example.com'

    link = Link(css='.link')
    link._fixed_target = mock_web_element

    result = link.url

    mock_web_element.get_attribute.assert_called_once_with('href')
    assert result == 'https://example.com'


def test_link_inherits_from_button():
    link = Link(css='.link')
    assert isinstance(link, Button)
