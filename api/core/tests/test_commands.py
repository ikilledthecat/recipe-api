
from django.core.management import call_command
from django.db.utils import OperationalError, ConnectionHandler


def test_wait_for_db_ready(mocker):
    """Test waiting for db when database is available"""
    mocker.patch(
        'django.db.utils.ConnectionHandler.__getitem__',
        return_value=True
    )
    call_command('wait_for_db')
    ConnectionHandler.__getitem__.assert_called_once()


def test_wait_for_db(mocker):
    """Test waiting for db when database is not available"""
    mocker.patch('time.sleep', return_value=True)
    mocker.patch(
        'django.db.utils.ConnectionHandler.__getitem__',
        side_effect=[OperationalError] * 5 + [True]
    )
    call_command('wait_for_db')
    ConnectionHandler.__getitem__.call_count == 6
