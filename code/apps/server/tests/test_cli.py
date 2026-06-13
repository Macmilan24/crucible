"""Tests for the `crucible` CLI and the model downloader (no network, no GPU)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from crucible_server.cli import main
from crucible_server.download import _human, download_model


def test_human_sizes() -> None:
    assert _human(512) == "512.0 B"
    assert _human(1536) == "1.5 KB"
    assert _human(1_929_903_264).endswith("GB")


def test_version_and_doctor_return_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["version"]) == 0
    assert "crucible" in capsys.readouterr().out
    assert main(["doctor"]) == 0  # reports env; never raises


def test_no_command_prints_help_and_returns_one() -> None:
    assert main([]) == 1


def test_serve_missing_model_returns_two(tmp_path: Path) -> None:
    missing = tmp_path / "nope.gguf"
    assert main(["serve", "--model", str(missing)]) == 2


def test_download_skips_when_present(tmp_path: Path) -> None:
    (tmp_path / "m.gguf").write_bytes(b"already here")
    out = download_model(tmp_path, url="http://example/x", name="m.gguf")
    assert out.read_bytes() == b"already here"  # untouched, no fetch attempted


class _FakeResp:
    """A minimal stand-in for an HTTP response (context-manager + chunked read)."""

    def __init__(self, data: bytes, status: int = 200) -> None:
        self._data = data
        self.status = status
        self.headers = {"Content-Length": str(len(data))}
        self._pos = 0

    def read(self, n: int) -> bytes:
        chunk = self._data[self._pos : self._pos + n]
        self._pos += len(chunk)
        return chunk

    def __enter__(self) -> _FakeResp:
        return self

    def __exit__(self, *_: object) -> bool:
        return False


def test_download_streams_to_disk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    payload = b"hello crucible" * 1000

    def fake_urlopen(_req: Any) -> _FakeResp:
        return _FakeResp(payload)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    out = download_model(tmp_path, url="http://example/model.gguf", name="model.gguf")
    assert out.read_bytes() == payload
    assert not (tmp_path / "model.gguf.part").exists()  # .part renamed on success
