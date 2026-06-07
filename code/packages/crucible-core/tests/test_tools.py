from __future__ import annotations

from pathlib import Path

import pytest

from crucible_core import (
    ToolRegistry,
    calculator_tool,
    read_file_tool,
    safe_arithmetic,
)


def test_safe_arithmetic_evaluates() -> None:
    assert safe_arithmetic("23*47+19") == 1100.0
    assert safe_arithmetic("-(3+4)*2") == -14.0


def test_safe_arithmetic_rejects_code() -> None:
    for bad in ["__import__('os')", "foo", "len([1])", "1 if True else 2"]:
        with pytest.raises(ValueError, match=r"unsafe|unsupported|invalid|Name|Call"):
            safe_arithmetic(bad)


def test_calculator_tool_runs() -> None:
    tool = calculator_tool()
    assert tool.run({"expression": "2+2"}) == "4.0"


def test_read_file_sandbox(tmp_path: Path) -> None:
    (tmp_path / "note.txt").write_text("hello")
    tool = read_file_tool(tmp_path)
    assert tool.run({"path": "note.txt"}) == "hello"
    with pytest.raises(ValueError, match="escapes"):
        tool.run({"path": "../../../etc/passwd"})


def test_registry_describe() -> None:
    reg = ToolRegistry()
    reg.register(calculator_tool())
    assert reg.has("calculator")
    assert "calculator(expression)" in reg.describe()
    assert {s.name for s in reg.schemas()} == {"calculator"}
