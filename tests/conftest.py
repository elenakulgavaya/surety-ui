from unittest.mock import MagicMock, Mock

import sys

import pytest

from pathlib import Path


mock_config = MagicMock()
mock_config.Browser.headless = False
mock_config.Browser.get = Mock(return_value=None)
mock_config.Screenshot.compare = False
mock_config.Screenshot.threshold = 5.0
mock_config.__name__ = 'Cfg'

mock_config_module = MagicMock()
mock_config_module.Cfg = mock_config

sys.modules['surety.config'] = mock_config_module
sys.modules['surety.config.config'] = mock_config_module

from surety.ui.singleton import Singleton


@pytest.fixture
def reset_browser(monkeypatch):
    if hasattr(Singleton, '_instances'):
        Singleton._instances.clear()


@pytest.fixture
def mock_chrome_driver(monkeypatch, reset_browser):
    mock_driver = MagicMock()
    mock_driver.set_page_load_timeout = Mock()
    mock_driver.set_window_size = Mock()
    mock_driver.get_log = Mock(return_value=[])
    mock_driver.quit = Mock()
    mock_driver.execute_script = Mock()
    mock_driver.implicitly_wait = Mock()

    return mock_driver


@pytest.fixture
def mock_chrome_class(monkeypatch, mock_chrome_driver):
    mock_chrome = Mock(return_value=mock_chrome_driver)
    monkeypatch.setattr('surety.ui.browser.Chrome', mock_chrome)
    return mock_chrome


@pytest.fixture
def mock_cfg(monkeypatch):
    mock_config = MagicMock()
    mock_config.Browser.headless = False
    mock_config.Browser.get = Mock(return_value=None)
    monkeypatch.setattr('surety.ui.browser.Cfg', mock_config)

    return mock_config


@pytest.fixture
def mock_folder(monkeypatch):
    mock_fold = MagicMock()
    mock_path = MagicMock(spec=Path)
    mock_path.absolute.return_value = Path('/mock/downloads')
    mock_fold.generate_path = Mock(return_value=mock_path)
    monkeypatch.setattr('surety.ui.browser.folder', mock_fold)

    return mock_fold

