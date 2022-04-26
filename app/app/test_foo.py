from app.calc import add
from app.calc import subtract
from django.test import TestCase


class TestCalc(TestCase):
    def test_add(self) -> None:
        self.assertEqual(add(1, 1), 2)

    def test_subtract(self) -> None:
        self.assertEqual(subtract(2, 1), 1)
