# Architecture Decision Records

An ADR captures a single architecturally-significant decision: its context, the options, the choice, and the consequences. We use a lightweight [MADR](https://adr.github.io/madr/)-style format.

**Rule:** code that contradicts an accepted ADR must update the ADR first. Decisions are reversible, but reversing one is itself a new ADR (supersede, don't silently drift).

## Status values
`proposed` · `accepted` · `superseded by ADR-XXXX` · `deprecated`

## Index

| # | Title | Status |
|---|---|---|
| [0001](0001-inference-native-co-location.md) | Inference-native co-location with separate fault domains | accepted |
| [0002](0002-monorepo-now-polyrepo-later.md) | Monorepo now, polyrepo-ready package boundaries | accepted |
| [0003](0003-inference-engine-sglang.md) | SGLang as the inference engine of record | accepted |
| [0004](0004-grammar-two-phase-decoding.md) | XGrammar-2 + two-phase decoding (constrain emission, not cognition) | accepted |
| [0005](0005-token-saver-as-true-subset.md) | The 0b token-saver is a true subset of Product 1 | accepted |
| [0006](0006-language-and-tooling.md) | Python 3.11+ and the toolchain baseline | accepted |
| [0007](0007-local-storage-sqlite-vector.md) | SQLite + vector index for all local stores | accepted |
| [0008](0008-licensing-open-core.md) | Open-core licensing, private-until-launch | accepted |
| [0009](0009-evaluation-as-product-gate.md) | Evaluation is the product gate (science = business) | accepted |
| [0010](0010-kv-cache-reuse-llamacpp.md) | KV-cache reuse on llama.cpp (Mac): same-model prefix reuse | accepted |

To add one: copy [`_template.md`](_template.md), take the next number, add a row here.
