from contextlib import suppress


__version__ = "0.0.13"


with suppress(ModuleNotFoundError):
    from django_stubs_ext import monkeypatch

    monkeypatch()
