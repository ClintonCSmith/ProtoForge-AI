def test_health() -> None:
    from src.main import health
    body = health()
    assert body["status"] == "ok"
    assert body["synthetic_data_only"] is True
