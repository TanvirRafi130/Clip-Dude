# Copyright (c) 2026 Tanvir. ClipDude project tests.
"""Local-only host/origin protections prevent DNS rebinding and cross-site actions."""
import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(main, "_jobs", {})
    monkeypatch.setattr(main._pool, "submit", lambda *args: None)
    return TestClient(main.app)


@pytest.mark.parametrize("host", ["evil.example:8765", "evil.example", "127.0.0.1.evil.example:8765", "192.168.1.5:8765"])
def test_rebound_hostnames_are_refused(client, host):
    bad = TestClient(main.app, base_url=f"http://{host}")
    origin = f"http://{host}"
    assert bad.post("/api/jobs", json={"url": "https://www.youtube.com/watch?v=abc123"}, headers={"Origin": origin}).status_code == 403
    assert bad.get("/api/jobs").status_code == 403
    assert bad.get("/api/models").status_code == 403


@pytest.mark.parametrize("host", ["127.0.0.1:8765", "localhost:8765", "127.0.0.1"])
def test_local_addresses_work(client, host):
    local = TestClient(main.app, base_url=f"http://{host}")
    assert local.get("/api/jobs").status_code == 200
    assert local.post("/api/jobs", json={"url": "https://www.youtube.com/watch?v=abc123"}, headers={"Origin": f"http://{host}"}).status_code == 200
