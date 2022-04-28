from contextlib import suppress


__version__ = "0.0.10"


with suppress(ModuleNotFoundError):
    from django_stubs_ext import monkeypatch

    monkeypatch()
