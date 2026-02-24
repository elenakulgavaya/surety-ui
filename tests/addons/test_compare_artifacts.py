from unittest.mock import patch

from surety.ui.pytest_addons import compare_screenshot, compare_downloaded_img


# pylint: disable=unused-argument

@patch('surety.ui.pytest_addons.Cfg')
@patch('surety.ui.pytest_addons.PageScreenshot')
@patch('surety.ui.pytest_addons.Browser')
def test_compare_screenshot_enabled(mock_browser, mock_page_screenshot,
                                    mock_cfg):
    mock_cfg.Screenshot.compare = True
    mock_page_screenshot.completed = False

    @compare_screenshot
    def test_func():
        pass

    test_func()

    expected_name = f'{test_func.__module__}.test_func.png'
    mock_page_screenshot.initialize.assert_called_once_with(expected_name)
    mock_page_screenshot.compare.assert_called_once_with(
        mock_browser.return_value.driver
    )


@patch('surety.ui.pytest_addons.Cfg')
@patch('surety.ui.pytest_addons.PageScreenshot')
def test_compare_screenshot_disabled(mock_page_screenshot, mock_cfg):
    mock_cfg.Screenshot.compare = False

    @compare_screenshot
    def test_func():
        pass

    test_func()

    mock_page_screenshot.initialize.assert_not_called()
    mock_page_screenshot.compare.assert_not_called()


@patch('surety.ui.pytest_addons.Cfg')
@patch('surety.ui.pytest_addons.PageScreenshot')
@patch('surety.ui.pytest_addons.Browser')
def test_compare_screenshot_completed(mock_browser, mock_page_screenshot,
                                      mock_cfg):
    mock_cfg.Screenshot.compare = True
    mock_page_screenshot.completed = True

    @compare_screenshot
    def test_func():
        pass

    test_func()

    mock_page_screenshot.compare.assert_not_called()


@patch('surety.ui.pytest_addons.Cfg')
@patch('surety.ui.pytest_addons.PageScreenshot')
@patch('surety.ui.pytest_addons.Browser')
def test_compare_screenshot_function_metadata(mock_browser,
                                              mock_page_screenshot, mock_cfg):
    mock_cfg.Screenshot.compare = False

    @compare_screenshot
    def test_func():
        """Test docstring"""
        pass

    assert test_func.__name__ == 'test_func'
    assert test_func.__doc__ == 'Test docstring'


@patch('surety.ui.pytest_addons.Cfg')
@patch('surety.ui.pytest_addons.DownloadedImg')
def test_compare_img_enabled(mock_downloaded_img, mock_cfg):
    mock_cfg.Screenshot.compare = True

    @compare_downloaded_img
    def test_func():
        pass

    test_func()

    expected_name = f'{test_func.__module__}.test_func.png'
    mock_downloaded_img.initialize.assert_called_once_with(expected_name)
    mock_downloaded_img.compare.assert_called_once()


@patch('surety.ui.pytest_addons.Cfg')
@patch('surety.ui.pytest_addons.DownloadedImg')
def test_compare_img_disabled(mock_downloaded_img, mock_cfg):
    mock_cfg.Screenshot.compare = False

    @compare_downloaded_img
    def test_func():
        pass

    test_func()

    mock_downloaded_img.initialize.assert_not_called()
    mock_downloaded_img.compare.assert_not_called()


@patch('surety.ui.pytest_addons.Cfg')
@patch('surety.ui.pytest_addons.DownloadedImg')
def test_compare_img_always_compares_if_enabled(mock_downloaded_img, mock_cfg):
    mock_cfg.Screenshot.compare = True

    @compare_downloaded_img
    def test_func():
        pass

    test_func()

    mock_downloaded_img.compare.assert_called_once()
