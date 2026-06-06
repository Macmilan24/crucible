# calculator 🟢 — Phase 0 (0c)

The public token calculator: paste your monthly agent token spend, see the projected
saving (anchored to 0a's measured reduction factors), join the waitlist. The top of
the funnel.

- PRD: [`../../../docs/product/0c-calculator.md`](../../../docs/product/0c-calculator.md)

**Not a Python package** (so it is intentionally excluded from the uv workspace
members). It is a small web front-end; the stack is TBD and will get its own ADR
when we build it. This folder is a placeholder so the funnel artifact has a home.

Hard requirements when built:
- Projections traceable to 0a's **published** reduction factors (assumptions shown — honesty is the brand).
- Loads fast, mobile-friendly, usable in < 10s.
- Waitlist capture; shareable result; no dark patterns.
