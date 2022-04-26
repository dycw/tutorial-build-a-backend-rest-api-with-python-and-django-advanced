from itertools import chain
from unittest.mock import MagicMock
from unittest.mock import patch

from beartype import beartype
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class TestCommand(TestCase):
    @beartype
    def test_wait_for_db_ready(self) -> None:
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.return_value = True
            _ = call_command("wait_for_db")
            self.assertEqual(gi.call_count, 1)

    @beartype
    @patch("time.sleep", return_value=True)
    def test_wait_for_db_waiting(self, _ts: MagicMock) -> None:
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.side_effect = list(chain(5 * [OperationalError], [True]))
            _ = call_command("wait_for_db")
            self.assertEqual(gi.call_count, 6)
