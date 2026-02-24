from unittest.mock import Mock

from surety.ui.elements import Table


def test_table_read_data():
    mock_head1 = Mock()
    mock_head1.text = 'Name'
    mock_head2 = Mock()
    mock_head2.text = 'Age'

    mock_col1_row1 = Mock()
    mock_col1_row1.text = 'Alice'
    mock_col2_row1 = Mock()
    mock_col2_row1.text = '30'

    mock_col1_row2 = Mock()
    mock_col1_row2.text = 'Bob'
    mock_col2_row2 = Mock()
    mock_col2_row2.text = '25'

    mock_row1 = Mock()
    mock_row1.Columns = [mock_col1_row1, mock_col2_row1]
    mock_row2 = Mock()
    mock_row2.Columns = [mock_col1_row2, mock_col2_row2]

    table = Table(css='table')
    table.Head = [mock_head1, mock_head2]
    table.Rows = [mock_row1, mock_row2]

    headers, data = table.read_data()

    assert headers == ['Name', 'Age']
    assert data == [['Alice', '30'], ['Bob', '25']]
