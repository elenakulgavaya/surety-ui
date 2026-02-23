import os
import shutil
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from PIL import Image

from surety.ui.screenshots import (
    CompareBase,
    Screenshot,
    PageScreenshot,
    DownloadedImg,
)


@pytest.fixture
def mock_cfg(monkeypatch):
    mock_config = MagicMock()
    mock_config.Screenshot.threshold = 5.0
    monkeypatch.setattr('surety.ui.screenshots.Cfg', mock_config)
    return mock_config



@patch('surety.ui.screenshots.folder.generate_file_path')
def test_compare_base_init_sets_file_paths(mock_generate_path):
    mock_generate_path.side_effect = [
        '/path/to/failed.png',
        '/path/to/threshold.png'
    ]

    compare_base = CompareBase('test.png')

    assert compare_base.file_name == 'test.png'
    assert compare_base.failed_screenshot == '/path/to/failed.png'
    assert compare_base.threshold_screenshot == '/path/to/threshold.png'


@patch('surety.ui.screenshots.Image.open')
@patch('surety.ui.screenshots.folder.generate_file_path')
def test_compare_base_with_identical_images(mock_generate_path, mock_image_open, mock_cfg):
    compare_base = CompareBase('test.png')

    # Create mock images with identical pixels
    mock_expected_img = Mock()
    mock_expected_img.size = (2, 2)
    mock_expected_img.getpixel.return_value = (255, 0, 0, 255)  # Red pixel

    mock_actual_img = Mock()
    mock_actual_img.size = (2, 2)
    mock_actual_img.getpixel.return_value = (255, 0, 0, 255)  # Same red pixel

    mock_image_open.side_effect = [mock_expected_img, mock_actual_img]

    mismatch = compare_base.base_compare('/fake/expected.png', '/fake/actual.png')

    assert mismatch == 0


@patch('surety.ui.screenshots.Image.open')
@patch('surety.ui.screenshots.folder.generate_file_path')
def test_compare_base_with_different_images(mock_generate_path, mock_image_open, mock_cfg):
    mock_generate_path.side_effect = [
        '/tmp/failed_test.png',
        '/tmp/threshold_test.png'
    ]
    compare_base = CompareBase('test.png')

    # Create mock images with different pixels
    mock_expected_img = Mock()
    mock_expected_img.size = (2, 2)
    mock_expected_img.getpixel.return_value = (0, 0, 0, 255)

    mock_actual_img = Mock()
    mock_actual_img.size = (2, 2)
    mock_actual_img.getpixel.return_value = (0, 0, 255, 255)

    mock_image_open.side_effect = [mock_expected_img, mock_actual_img]

    mismatch = compare_base.base_compare('/fake/expected.png', '/fake/actual.png')

    assert mismatch > 0


@patch('surety.ui.screenshots.Image.open')
@patch('surety.ui.screenshots.folder.generate_file_path')
def test_compare_base_saves_failed_screenshot_above_threshold(
    mock_generate_path, mock_image_open, mock_cfg
):
    mock_cfg.Screenshot.threshold = 1.0
    failed_path = '/tmp/failed_screenshot.png'
    mock_generate_path.side_effect = [failed_path, '/tmp/threshold.png']
    compare_base = CompareBase('test.png')

    mock_expected_img = Mock()
    mock_expected_img.size = (2, 2)
    mock_expected_img.getpixel.return_value = (0, 0, 0, 255)

    mock_actual_img = Mock()
    mock_actual_img.size = (2, 2)
    mock_actual_img.getpixel.return_value = (0, 0, 255, 255)
    mock_actual_img.save = Mock()

    mock_image_open.side_effect = [mock_expected_img, mock_actual_img]

    compare_base.base_compare('/fake/expected.png', '/fake/actual.png')

    # Verify that save was called (indicating failed screenshot was saved)
    mock_actual_img.save.assert_called_once_with(failed_path)


@patch('surety.ui.screenshots.Image.open')
@patch('surety.ui.screenshots.folder.generate_file_path')
def test_compare_base_saves_threshold_screenshot_below_threshold(
    mock_generate_path, mock_image_open, mock_cfg
):
    mock_cfg.Screenshot.threshold = 100.0
    threshold_path = '/tmp/threshold_screenshot.png'
    mock_generate_path.side_effect = ['/tmp/failed.png', threshold_path]
    compare_base = CompareBase('test.png')

    mock_expected_img = Mock()
    mock_expected_img.size = (2, 2)
    mock_expected_img.getpixel.return_value = (0, 0, 150, 255)

    mock_actual_img = Mock()
    mock_actual_img.size = (2, 2)
    mock_actual_img.getpixel.return_value = (0, 0, 255, 255)
    mock_actual_img.save = Mock()

    mock_image_open.side_effect = [mock_expected_img, mock_actual_img]

    compare_base.base_compare('/fake/expected.png', '/fake/actual.png')

    # Verify that save was called with threshold path (mismatch > 0 but < 90%)
    mock_actual_img.save.assert_called_once_with(threshold_path)


def test_compare_base_process_pixel_returns_value():
    img = Image.new('RGB', (2, 2), color=(100, 150, 200))
    result = CompareBase.process_pixel(img, 1, 1)
    assert result == 11.25


def test_compare_base_process_pixel_handles_invalid_coordinates():
    img = Image.new('RGB', (2, 2), color='red')
    result = CompareBase.process_pixel(img, 100, 100)
    assert result is None



@patch('surety.ui.screenshots.folder.generate_file_path')
def test_screenshot_init_parses_test_name_correctly(mock_generate_path):
    mock_generate_path.side_effect = [
        '/tmp/failed.png',
        '/tmp/threshold.png',
        '/tmp/actual.png',
        '/tmp/expected.png'
    ]

    target = Mock()
    screenshot = Screenshot(target, 'module.suite.test_function.png')

    assert screenshot.expected_folder == 'suite'
    assert screenshot.expected_file == 'test_function.png'


@patch('surety.ui.screenshots.folder.generate_file_path')
def test_screenshot_init_handles_extra_suffix(mock_generate_path):
    mock_generate_path.side_effect = [
        '/tmp/failed.png',
        '/tmp/threshold.png',
        '/tmp/actual.png',
        '/tmp/expected.png'
    ]

    target = Mock()
    screenshot = Screenshot(target, 'module.suite_extra.test_function.png')

    assert screenshot.expected_folder == 'suite'


@patch('surety.ui.screenshots.folder.generate_file_path')
def test_screenshot_init_handles_reports_suffix(mock_generate_path):
    mock_generate_path.side_effect = [
        '/tmp/failed.png',
        '/tmp/threshold.png',
        '/tmp/actual.png',
        '/tmp/expected.png'
    ]

    target = Mock()
    screenshot = Screenshot(target, 'module.suite_reports.test_function.png')

    assert screenshot.expected_folder == 'suite'


@patch('surety.ui.screenshots.folder.generate_file_path')
def test_screenshot_take_saves_screenshot(mock_generate_path):
    mock_generate_path.side_effect = [
        '/tmp/failed.png',
        '/tmp/threshold.png',
        '/tmp/actual.png',
        '/tmp/expected.png'
    ]

    target = Mock()
    screenshot = Screenshot(target, 'module.suite.test.png')
    screenshot.take()

    target.save_screenshot.assert_called_once_with('/tmp/actual.png')
    target.get_screenshot_as_png.assert_called_once()


@patch('surety.ui.screenshots.folder.generate_file_path')
def test_screenshot_generate_expected_saves_screenshot(mock_generate_path):
    mock_generate_path.side_effect = [
        '/tmp/failed.png',
        '/tmp/threshold.png',
        '/tmp/actual.png',
        '/tmp/expected.png'
    ]

    target = Mock()
    screenshot = Screenshot(target, 'module.suite.test.png')
    screenshot.generate_expected()

    target.save_screenshot.assert_called_once_with('/tmp/expected.png')
    target.get_screenshot_as_png.assert_called_once()


@patch('surety.ui.screenshots.folder.generate_file_path')
@patch('surety.ui.screenshots.Image.open')
def test_screenshot_compare_raises_when_expected_missing(mock_image_open, mock_generate_path):
    mock_generate_path.side_effect = [
        '/tmp/failed.png',
        '/tmp/threshold.png',
        '/tmp/actual.png',
        '/tmp/expected_missing.png'
    ]
    mock_image_open.side_effect = FileNotFoundError()

    target = Mock()
    screenshot = Screenshot(target, 'module.suite.test.png')

    with pytest.raises(FileNotFoundError, match='Expected screenshot is missing'):
        screenshot.compare()

    target.save_screenshot.assert_called_once()


@patch('surety.ui.screenshots.Image.open')
@patch('surety.ui.screenshots.folder.generate_file_path')
def test_screenshot_compare_returns_mismatch_percentage(mock_generate_path, mock_image_open, mock_cfg):
    mock_generate_path.side_effect = [
        '/tmp/failed.png',
        '/tmp/threshold.png',
        '/tmp/actual_compare.png',
        '/tmp/expected_compare.png'
    ]


    mock_expected_img = Mock()
    mock_expected_img.size = (2, 2)
    mock_expected_img.getpixel.return_value = (0, 0, 0, 255)

    mock_actual_img = Mock()
    mock_actual_img.size = (2, 2)
    mock_actual_img.getpixel.return_value = (0, 0, 0, 255)
    mock_actual_img.save = Mock()

    mock_image_open.side_effect = [
        mock_expected_img, mock_expected_img, mock_actual_img
    ]


    target = Mock()
    screenshot = Screenshot(target, 'module.suite.test.png')
    mismatch = screenshot.compare()

    assert mismatch == 0



def test_page_screenshot_initial_state():
    assert PageScreenshot.save_mode is False


def test_page_screenshot_set_save_mode():
    PageScreenshot.set_save_mode(True)
    assert PageScreenshot.save_mode is True

    PageScreenshot.set_save_mode(False)
    assert PageScreenshot.save_mode is False


def test_page_screenshot_initialize():
    PageScreenshot.initialize('test.png')
    assert PageScreenshot.name == 'test.png'
    assert PageScreenshot.completed is False


def test_page_screenshot_complete():
    PageScreenshot.initialize('test.png')
    PageScreenshot.complete()
    assert PageScreenshot.name is None
    assert PageScreenshot.completed is True


@patch('surety.ui.screenshots.Screenshot')
def test_page_screenshot_compare_in_save_mode(mock_screenshot_cls, mock_cfg):
    PageScreenshot.save_mode = True
    PageScreenshot.completed = False
    PageScreenshot.name = 'test.png'

    mock_screenshot = Mock()
    mock_screenshot_cls.return_value = mock_screenshot

    target = Mock()
    PageScreenshot.compare(target)

    mock_screenshot.generate_expected.assert_called_once()
    mock_screenshot.take.assert_not_called()
    assert PageScreenshot.completed is True


@patch('surety.ui.screenshots.Screenshot')
def test_page_screenshot_compare_in_normal_mode(mock_screenshot_cls, mock_cfg):
    PageScreenshot.save_mode = False
    PageScreenshot.completed = False
    PageScreenshot.name = 'test.png'

    mock_screenshot = Mock()
    mock_screenshot.compare.return_value = 0
    mock_screenshot_cls.return_value = mock_screenshot

    target = Mock()
    PageScreenshot.compare(target)

    mock_screenshot.take.assert_called_once()
    mock_screenshot.compare.assert_called_once()
    assert PageScreenshot.completed is True


@patch('surety.ui.screenshots.Screenshot')
def test_page_screenshot_compare_fails_above_threshold(
    mock_screenshot_cls, mock_cfg
):
    PageScreenshot.save_mode = False
    PageScreenshot.completed = False
    PageScreenshot.name = 'test.png'

    mock_screenshot = Mock()
    mock_screenshot.compare.return_value = 10.0
    mock_screenshot_cls.return_value = mock_screenshot

    target = Mock()

    with pytest.raises(AssertionError, match="Screenshots don't match"):
        PageScreenshot.compare(target)



def test_downloaded_img_initial_state():
    assert DownloadedImg.save_mode is False


def test_downloaded_img_set_save_mode():
    DownloadedImg.set_save_mode(True)
    assert DownloadedImg.save_mode is True

    DownloadedImg.set_save_mode(False)
    assert DownloadedImg.save_mode is False


@patch('surety.ui.screenshots.shutil.rmtree')
@patch('surety.ui.screenshots.folder.generate_path')
def test_downloaded_img_initialize_clears_downloads(mock_generate_path, mock_rmtree):
    mock_path = Mock()
    mock_path.absolute.return_value = '/tmp/downloads'
    mock_generate_path.return_value = mock_path

    DownloadedImg.initialize('test.png')

    mock_rmtree.assert_called_once_with('/tmp/downloads', ignore_errors=True)
    assert DownloadedImg.name == 'test.png'


@patch('surety.ui.screenshots.folder.generate_path')
@patch('surety.ui.screenshots.os.listdir')
def test_downloaded_img_get_file_finds_png(mock_listdir, mock_generate_path):
    mock_path = Mock()
    mock_path.absolute.return_value = '/tmp/downloads'
    mock_generate_path.return_value = mock_path
    mock_listdir.side_effect = [
        ['file.txt'],
        ['file.png'],
        ['file.png']
    ]

    result = DownloadedImg.get_downloaded_file_with_wait()

    assert result == '/tmp/downloads/file.png'


@patch('surety.ui.screenshots.folder.generate_path')
@patch('surety.ui.screenshots.os.listdir')
@patch('surety.ui.screenshots.wait')
def test_downloaded_img_get_file_returns_none_when_no_files(
    mock_wait, mock_listdir, mock_generate_path
):
    mock_path = Mock()
    mock_path.absolute.return_value = '/tmp/downloads'
    mock_generate_path.return_value = mock_path
    mock_listdir.return_value = []

    result = DownloadedImg.get_downloaded_file_with_wait()

    assert result is None


def test_downloaded_img_complete():
    DownloadedImg.name = 'test.png'
    DownloadedImg.complete()
    assert DownloadedImg.name is None


@patch('surety.ui.screenshots.folder.generate_file_path')
@patch('surety.ui.screenshots.DownloadedImg.get_downloaded_file_with_wait')
@patch('surety.ui.screenshots.shutil.copy')
def test_downloaded_img_compare_in_save_mode(
    mock_copy, mock_get_file, mock_generate_path, mock_cfg
):
    DownloadedImg.save_mode = True
    DownloadedImg.name = 'module.suite.test.png'

    mock_get_file.return_value = '/tmp/downloaded.png'
    mock_generate_path.return_value = '/tmp/expected.png'

    DownloadedImg.compare()

    mock_copy.assert_called_once_with('/tmp/downloaded.png', '/tmp/expected.png')
    assert DownloadedImg.name is None


@patch('surety.ui.screenshots.folder.generate_file_path')
@patch('surety.ui.screenshots.DownloadedImg.get_downloaded_file_with_wait')
@patch('surety.ui.screenshots.shutil.copy')
@patch('surety.ui.screenshots.CompareBase')
def test_downloaded_img_compare_in_normal_mode(
    mock_compare_base_cls, mock_copy, mock_get_file, mock_generate_path,
    mock_cfg):
    mock_cfg.Screenshot.threshold = 5.0
    DownloadedImg.save_mode = False
    DownloadedImg.name = 'module.suite.test.png'

    mock_get_file.return_value = '/tmp/downloaded.png'
    mock_generate_path.side_effect = [
        '/tmp/expected.png',
        '/tmp/actual.png'
    ]

    mock_compare_base = Mock()
    mock_compare_base.base_compare.return_value = 0
    mock_compare_base_cls.return_value = mock_compare_base

    DownloadedImg.compare()

    mock_compare_base.base_compare.assert_called_once()
    mock_copy.assert_called_once_with('/tmp/downloaded.png', '/tmp/actual.png')
    assert DownloadedImg.name is None


@patch('surety.ui.screenshots.folder.generate_file_path')
@patch('surety.ui.screenshots.DownloadedImg.get_downloaded_file_with_wait')
@patch('surety.ui.screenshots.shutil.copy')
@patch('surety.ui.screenshots.CompareBase')
def test_downloaded_img_compare_fails_above_threshold(
    mock_compare_base_cls, mock_copy, mock_get_file, mock_generate_path,
    mock_cfg):
    mock_cfg.Screenshot.threshold = 5.0
    DownloadedImg.save_mode = False
    DownloadedImg.name = 'module.suite.test.png'

    mock_get_file.return_value = '/tmp/downloaded.png'
    mock_generate_path.side_effect = [
        '/tmp/expected.png',
        '/tmp/actual.png'
    ]

    mock_compare_base = Mock()
    mock_compare_base.base_compare.return_value = 10.0
    mock_compare_base_cls.return_value = mock_compare_base

    with pytest.raises(AssertionError, match="Files don't match"):
        DownloadedImg.compare()
