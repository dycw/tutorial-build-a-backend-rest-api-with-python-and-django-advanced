from app.calc import add
from django.test import TestCase


class TestAdd(TestCase):
    def test_add(self) -> None:
        self.assertEqual(add(1, 1), 3)
