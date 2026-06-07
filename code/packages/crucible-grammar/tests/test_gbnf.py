from __future__ import annotations

import pytest

from crucible_grammar import ToolSchema, is_valid_tool_call, tool_call_gbnf

WEATHER = ToolSchema(name="get_weather", params=("city", "units"))


def test_gbnf_mentions_name_and_params() -> None:
    g = tool_call_gbnf(WEATHER)
    assert "get_weather" in g
    assert "city" in g and "units" in g
    assert g.startswith("root")


def test_valid_call_accepted() -> None:
    text = '{"tool": "get_weather", "arguments": {"city": "Paris", "units": "c"}}'
    assert is_valid_tool_call(text, WEATHER)


def test_wrong_tool_name_rejected() -> None:
    text = '{"tool": "set_weather", "arguments": {"city": "Paris", "units": "c"}}'
    assert not is_valid_tool_call(text, WEATHER)


def test_missing_arg_rejected() -> None:
    assert not is_valid_tool_call(
        '{"tool": "get_weather", "arguments": {"city": "Paris"}}', WEATHER
    )


def test_extra_arg_rejected() -> None:
    text = '{"tool": "get_weather", "arguments": {"city": "P", "units": "c", "x": 1}}'
    assert not is_valid_tool_call(text, WEATHER)


def test_unparseable_rejected() -> None:
    assert not is_valid_tool_call("get_weather(Paris, c)  # not json", WEATHER)


def test_schema_validation() -> None:
    with pytest.raises(ValueError, match="at least one parameter"):
        ToolSchema(name="x", params=())
