"""The benchmark task suite.

Two kinds of task:
- ReasoningTask: a question with a known integer answer (for the token-economy arm).
- ToolTask: an instruction + a tool schema (for the malformed-rate arm). The schema
  is deliberately non-trivial (4 fields) so an unconstrained small model actually
  trips up sometimes — which is where grammar-scoped emission shows its value.

This is a small, runnable-now suite — NOT SWE-bench. The publishable headline needs
the big contamination-resistant suites + a 7B+ model (docs/05-evaluation-plan.md).
"""

from __future__ import annotations

from dataclasses import dataclass

from crucible_grammar import ToolSchema


@dataclass(frozen=True, slots=True)
class ReasoningTask:
    question: str
    answer: int


@dataclass(frozen=True, slots=True)
class ToolTask:
    name: str
    instruction: str
    schema: ToolSchema


REASONING_TASKS: list[ReasoningTask] = [
    ReasoningTask(
        "Natalia sold clips to 48 friends in April, and half as many in May. "
        "How many clips did she sell altogether?",
        72,
    ),
    ReasoningTask(
        "Weng earns $12 per hour for babysitting. Yesterday she babysat for 60 minutes. "
        "How many dollars did she earn?",
        12,
    ),
    ReasoningTask(
        "A robe takes 2 bolts of blue fiber and half that much white fiber. "
        "How many bolts in total does it take?",
        3,
    ),
    ReasoningTask(
        "There are 15 trees. Workers plant more so there are 21 trees. "
        "How many trees did they plant?",
        6,
    ),
    ReasoningTask(
        "Shawn has 5 toys. For Christmas he got 2 toys each from mom and dad. "
        "How many toys does he have now?",
        9,
    ),
    ReasoningTask(
        "A school has 4 classrooms. Each classroom has 6 rows of 5 desks. "
        "How many desks are there in total?",
        120,
    ),
]

# A 4-field schema — small models often drop a field, add prose, or wrap in markdown.
_EVENT = ToolSchema("create_event", ("title", "date", "time", "location"))

TOOL_TASKS: list[ToolTask] = [
    ToolTask(
        "q3review",
        "Schedule a meeting titled 'Q3 Review' on 2026-07-01 at 14:00 in Room B. "
        "Use the create_event tool.",
        _EVENT,
    ),
    ToolTask(
        "standup",
        "Please set up our daily standup called 'Standup' for 2026-06-15, 09:30, in the Main Hall.",
        _EVENT,
    ),
    ToolTask(
        "launch",
        "I need an event on the calendar: the 'Launch Party', date 2026-08-20, "
        "time 18:00, at the Rooftop.",
        _EVENT,
    ),
    ToolTask(
        "interview",
        "Book 'Candidate Interview' for July 3rd 2026 at 11 in the morning, Room 12.",
        _EVENT,
    ),
]
