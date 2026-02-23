from pathlib import Path
from unittest.mock import patch, Mock, call
from surety.ui.folder import (
    generate_path,
    generate_file_name,
    generate_file_path,
    get_downloaded_file_with_wait
)


@patch('surety.ui.folder.os.makedirs')
@patch('surety.ui.folder.os.path.exists')
def test_generate_path_not_exists(mock_exists, mock_makedirs):
    mock_exists.return_value = False

    result = generate_path('test_folder')

    assert isinstance(result, Path)
    assert 'test_folder' in str(result)
    mock_exists.assert_called_once()
    mock_makedirs.assert_called_once()


@patch('surety.ui.folder.os.makedirs')
@patch('surety.ui.folder.os.path.exists')
def test_generate_path_when_exists(mock_exists, mock_makedirs):
    mock_exists.return_value = True

    result = generate_path('existing_folder')

    assert isinstance(result, Path)
    assert 'existing_folder' in str(result)
    mock_exists.assert_called_once()
    mock_makedirs.assert_not_called()


@patch('surety.ui.folder.os.makedirs')
@patch('surety.ui.folder.os.path.exists')
def test_generate_path_race_condition(mock_exists, mock_makedirs):
    mock_exists.return_value = False
    mock_makedirs.side_effect = FileExistsError('Directory already exists')

    result = generate_path('race_folder')

    assert isinstance(result, Path)
    assert 'race_folder' in str(result)
    mock_makedirs.assert_called_once()


@patch('surety.ui.folder.os.makedirs')
@patch('surety.ui.folder.os.path.exists')
def test_generate_path_with_nested_path(mock_exists, mock_makedirs):
    mock_exists.return_value = False

    result = generate_path('data/results/screenshots')

    assert isinstance(result, Path)
    assert 'data' in str(result)
    assert 'results' in str(result)
    assert 'screenshots' in str(result)
    mock_makedirs.assert_called_once()


@patch('surety.ui.folder.os.makedirs')
@patch('surety.ui.folder.os.path.exists')
def test_generate_path_returns_path_object(mock_exists, mock_makedirs):
    mock_exists.return_value = True

    result = generate_path('any_folder')

    assert isinstance(result, Path)



@patch('surety.ui.folder.datetime')
def test_generate_file_name_default_parameters(mock_datetime):
    mock_datetime.now.return_value.strftime.return_value = '20250221_143000'

    result = generate_file_name()

    assert result == '20250221_143000_.png'
    assert result.endswith('.png')
    mock_datetime.now.return_value.strftime.assert_called_once_with('%Y%m%d_%H%M%S')


@patch('surety.ui.folder.datetime')
def test_generate_file_name_with_postfix(mock_datetime):
    mock_datetime.now.return_value.strftime.return_value = '20250221_143000'

    result = generate_file_name(postfix='screenshot')

    assert result == '20250221_143000_screenshot.png'
    assert 'screenshot' in result
    assert result.endswith('.png')


@patch('surety.ui.folder.datetime')
def test_generate_file_name_with_custom_extension(mock_datetime):
    mock_datetime.now.return_value.strftime.return_value = '20250221_143000'

    result = generate_file_name(extension='jpg')

    assert result == '20250221_143000_.jpg'
    assert result.endswith('.jpg')


@patch('surety.ui.folder.datetime')
def test_generate_file_name_with_postfix_and_extension(mock_datetime):
    mock_datetime.now.return_value.strftime.return_value = '20250221_143000'

    result = generate_file_name(postfix='test_result', extension='pdf')

    assert result == '20250221_143000_test_result.pdf'
    assert 'test_result' in result
    assert result.endswith('.pdf')


@patch('surety.ui.folder.datetime')
def test_generate_file_name_includes_timestamp_format(mock_datetime):
    mock_datetime.now.return_value.strftime.return_value = '20250101_120000'

    result = generate_file_name(postfix='data')

    assert '20250101_120000' in result
    mock_datetime.now.return_value.strftime.assert_called_once_with('%Y%m%d_%H%M%S')


@patch('surety.ui.folder.generate_path')
def test_generate_file_path_folder_and_filename(mock_generate_path):
    mock_path = Path('screenshots')
    mock_generate_path.return_value = mock_path

    result = generate_file_path('screenshots', 'image.png')

    assert isinstance(result, str)
    assert 'screenshots' in result
    assert 'image.png' in result
    mock_generate_path.assert_called_once_with('screenshots')


@patch('surety.ui.folder.generate_path')
def test_generate_file_path_returns_string(mock_generate_path):
    mock_path = Path('test_folder')
    mock_generate_path.return_value = mock_path

    result = generate_file_path('test_folder', 'file.txt')

    assert isinstance(result, str)
    assert result == str(mock_path / 'file.txt')


@patch('surety.ui.folder.generate_path')
def test_generate_file_path_with_nested_folder(mock_generate_path):
    mock_path = Path('data/results')
    mock_generate_path.return_value = mock_path

    result = generate_file_path('data/results', 'report.pdf')

    assert 'data' in result
    assert 'results' in result
    assert 'report.pdf' in result


@patch('surety.ui.folder.generate_path')
def test_generate_file_path_calls_generate_path(mock_generate_path):
    mock_path = Path('downloads')
    mock_generate_path.return_value = mock_path

    generate_file_path('downloads', 'file.zip')

    mock_generate_path.assert_called_once_with('downloads')


@patch('surety.ui.folder.os.listdir')
@patch('surety.ui.folder.generate_path')
def test_get_downloaded_file_any(mock_generate_path, mock_listdir):
    mock_path = Mock()
    mock_path.absolute.return_value = '/fake/downloads'
    mock_generate_path.return_value = mock_path
    mock_listdir.side_effect = [['file.pdf'], ['file.pdf']]

    result = get_downloaded_file_with_wait()

    assert result == '/fake/downloads/file.pdf'
    mock_generate_path.assert_called_once_with('downloads')
    assert mock_listdir.call_count == 2


@patch('surety.ui.folder.wait')
@patch('surety.ui.folder.os.listdir')
@patch('surety.ui.folder.generate_path')
def test_get_downloaded_file_extension(mock_generate_path, mock_listdir,
                                       mock_wait):
    mock_path = Mock()
    mock_path.absolute.return_value = '/fake/downloads'
    mock_generate_path.return_value = mock_path
    mock_listdir.side_effect = [['file.pdf', 'other.txt'], ['file.pdf', 'other.txt']]

    result = get_downloaded_file_with_wait(extension='.pdf')

    assert result == '/fake/downloads/file.pdf'
    mock_wait.assert_called_once()


@patch('surety.ui.folder.wait')
@patch('surety.ui.folder.os.listdir')
@patch('surety.ui.folder.generate_path')
def test_get_downloaded_file_returns_first(mock_generate_path, mock_listdir,
                                           mock_wait):
    mock_path = Mock()
    mock_path.absolute.return_value = '/fake/downloads'
    mock_generate_path.return_value = mock_path
    mock_listdir.side_effect = [
        ['first.pdf', 'second.pdf'],
        ['first.pdf', 'second.pdf']
    ]

    result = get_downloaded_file_with_wait(extension='.pdf')

    assert result == '/fake/downloads/first.pdf'


@patch('surety.ui.folder.wait')
@patch('surety.ui.folder.os.listdir')
@patch('surety.ui.folder.generate_path')
def test_get_downloaded_file_with_wait_skips_ext(mock_generate_path,
                                                 mock_listdir, mock_wait):
    mock_path = Mock()
    mock_path.absolute.return_value = '/fake/downloads'
    mock_generate_path.return_value = mock_path

    # First call to listdir (inside wait_for_file): has .txt, no .pdf -> returns False
    # Second call: has .pdf -> returns True
    # Third call (after wait): returns the file
    mock_listdir.side_effect = [
        ['file.txt'],
        ['file.txt', 'document.pdf'],
        ['file.txt', 'document.pdf']
    ]

    result = get_downloaded_file_with_wait(extension='.pdf')

    assert result == '/fake/downloads/file.txt'


@patch('surety.ui.folder.wait')
@patch('surety.ui.folder.os.listdir')
@patch('surety.ui.folder.generate_path')
def test_get_downloaded_file_with_wait_calls_wait(mock_generate_path,
                                                  mock_listdir, mock_wait):
    mock_path = Mock()
    mock_path.absolute.return_value = '/fake/downloads'
    mock_generate_path.return_value = mock_path
    mock_listdir.side_effect = [['file.pdf'], ['file.pdf']]

    get_downloaded_file_with_wait()

    assert mock_wait.call_count == 1
    call_kwargs = mock_wait.call_args[1]
    assert call_kwargs['timeout_seconds'] == 2
    assert call_kwargs['waiting_for'] == 'file to download'


@patch('surety.ui.folder.wait')
@patch('surety.ui.folder.os.listdir')
@patch('surety.ui.folder.generate_path')
def test_get_downloaded_file_with_wait_no_files(mock_generate_path,
                                                mock_listdir, mock_wait):
    mock_path = Mock()
    mock_path.absolute.return_value = '/fake/downloads'
    mock_generate_path.return_value = mock_path
    mock_listdir.return_value = []

    result = get_downloaded_file_with_wait()

    assert result is None


@patch('surety.ui.folder.os.listdir')
@patch('surety.ui.folder.generate_path')
def test_get_downloaded_file_with_wait_no_ext_match(mock_generate_path,
                                                    mock_listdir):
    mock_path = Mock()
    mock_path.absolute.return_value = '/fake/downloads'
    mock_generate_path.return_value = mock_path
    mock_listdir.side_effect = [
        ['any_file.xyz'],  # wait_for_file should return True
        ['any_file.xyz']   # final iteration
    ]

    result = get_downloaded_file_with_wait(extension=None)

    assert result == '/fake/downloads/any_file.xyz'


@patch('surety.ui.folder.os.listdir')
@patch('surety.ui.folder.generate_path')
def test_get_downloaded_file_with_wait_no_match_return(mock_generate_path,
                                                       mock_listdir):
    mock_path = Mock()
    mock_path.absolute.return_value = '/fake/downloads'
    mock_generate_path.return_value = mock_path

    mock_listdir.side_effect = [
        ['file.txt', 'doc.docx'],
        ['file.txt', 'doc.docx', 'image.pdf'],
        ['file.txt', 'doc.docx', 'image.pdf']
    ]

    result = get_downloaded_file_with_wait(extension='.pdf')

    assert result == '/fake/downloads/file.txt'
