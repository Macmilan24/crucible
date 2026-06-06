# PRD 0c — The Public Token Calculator

> Converts the abstract thesis into *their* number. The top of the funnel: endlessly shareable, captures a waitlist.

## Pain

The token-cost crisis is abstract until a developer sees it in their own spend. They need a 10-second way to find out what Crucible would save *them*.

## What it is

A small web page where a developer pastes their monthly agent token spend (and a few parameters) and sees the **projected saving**, grounded in the benchmark's measured reduction factors.

## Users

Anyone feeling token-cost pain — developers, eng leads, CFOs. The shareable artifact that turns a tweet into a waitlist signup.

## Scope

- A single web page (`apps/calculator`): inputs (monthly spend / tokens, agent type, optional hard-task fraction) → projected saving with a clear, honest range.
- Numbers anchored to **0a's measured reductions** (no fabricated multipliers); show the assumptions.
- **Waitlist capture** (email).
- Shareable result (link/image).

## Out of scope

Account systems, billing, anything heavy. It is a funnel page, not a product surface.

## Aha demo

Paste "$1,800/month" → see the projected steady-state spend and savings, with the assumptions visible → join the waitlist.

## Acceptance criteria

- [ ] Loads fast; usable in under 10 seconds; mobile-friendly.
- [ ] Projections traceable to 0a's published reduction factors (with assumptions shown — honesty is the brand).
- [ ] Waitlist capture works and is measurable.
- [ ] Result is shareable (link or generated image).
- [ ] No dark patterns; the range is honest, including the "your mileage varies" caveat.

## Success metric

Waitlist size; share rate; conversion of calculator visitors → 0b installs.

## ⛔ Kill-criterion

Traffic doesn't convert to waitlist or installs (the message isn't landing) — revisit positioning, not just the page.

## Dependencies

Depends on **0a** for credible numbers. Feeds **0b** (installs) and the broader funnel:

```
benchmark + post + calculator (attention)
        ▼
 GitHub stars + waitlist
        ▼
 Core installs (free runtime)   ← 0b → P1
        ▼
 Pro upgrades → Team / Enterprise
```
