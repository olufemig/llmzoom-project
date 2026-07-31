from app import observability


def test_setup_observability_skips_without_api_key(monkeypatch):
    called = {"setup": False}

    monkeypatch.delenv("LANGWATCH_API_KEY", raising=False)
    monkeypatch.setattr(observability, "Client", lambda **kwargs: called.__setitem__("setup", True))

    observability.setup_observability()

    assert called["setup"] is False


def test_setup_observability_configures_langwatch(monkeypatch):
    captured = {}

    monkeypatch.setenv("LANGWATCH_API_KEY", "key")
    monkeypatch.setenv("LANGWATCH_ENDPOINT", "https://example.com")
    monkeypatch.setattr(
        observability,
        "Client",
        lambda **kwargs: captured.update(kwargs),
    )

    observability.setup_observability()

    assert captured["api_key"] == "key"
    assert captured["endpoint_url"] == "https://example.com"
    assert "instrumentors" in captured
