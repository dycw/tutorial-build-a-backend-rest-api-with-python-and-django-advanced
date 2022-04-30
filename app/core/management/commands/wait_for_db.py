import time  # to be mocked
from typing import Any

from django.core.management import BaseCommand
from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.utils import OperationalError


class Command(BaseCommand):
    def handle(self, *_args: Any, **_kwargs: Any) -> None:
        self.stdout.write("Waiting for database...")
        db_conn: BaseDatabaseWrapper | None = None
        while db_conn is None:
            try:
                db_conn = connections["default"]
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("Database available"))
