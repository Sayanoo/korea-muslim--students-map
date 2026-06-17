# tests/test_fetch_data.py
import os
from pipeline.fetch_data import download_bulk_xlsx


def test_download_writes_file(tmp_path, monkeypatch):
    # Stub the network call so the test is offline and deterministic.
    import pipeline.fetch_data as fd

    def fake_get(url, timeout):
        class R:
            status_code = 200
            content = b"PK\x03\x04fake-xlsx-bytes"

            def raise_for_status(self):
                pass

        return R()

    monkeypatch.setattr(fd.requests, "get", fake_get)
    path = download_bulk_xlsx(str(tmp_path))
    assert os.path.exists(path)
    assert path.endswith(".xlsx")
    assert os.path.getsize(path) > 0
