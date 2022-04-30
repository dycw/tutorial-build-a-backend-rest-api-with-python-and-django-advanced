from itertools import chain
from unittest.mock import patch

from beartype import beartype
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class TestCommand(TestCase):
    @beartype
    def test_wait_for_db_ready(self) -> None:
        with patch(
            "django.db.utils.ConnectionHandler.__getitem__", return_value=True
        ) as gi:
            _ = call_command("wait_for_db")
            self.assertEqual(gi.call_count, 1)

    @beartype
    def test_wait_for_db_waiting(self) -> None:
        with patch("time.sleep", return_value=True), patch(
            "django.db.utils.ConnectionHandler.__getitem__",
            side_effect=list(chain(5 * [OperationalError], [True])),
        ) as gi:
            _ = call_command("wait_for_db")
            self.assertEqual(gi.call_count, 6)
