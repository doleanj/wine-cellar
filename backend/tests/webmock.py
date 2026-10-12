"""Test helper: route httpx.AsyncClient (used by main.py) through a mock transport, no network."""
import httpx

_REAL = httpx.AsyncClient  # captured at import time, before any patching


def patch_web(monkeypatch, handler):
    import main
    monkeypatch.setattr(main.httpx, "AsyncClient",
                        lambda *a, **k: _REAL(*a, **{**k, "transport": httpx.MockTransport(handler)}))
