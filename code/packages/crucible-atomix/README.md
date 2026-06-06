# crucible-atomix 🟢

Safe, transactional tool execution with rollback — usable by any agent, and a true
spin-out candidate. Naive "execute then roll back" is unsafe under concurrency and
impossible for irreversible external effects; Atomix settles speculative actions so
an effect becomes permanent only when it is certified safe.

- Spec: [`../../../docs/02-architecture.md`](../../../docs/02-architecture.md) (Layer 1, Atomix transactional settlement)
- Glossary: Atomix, reversibility classes
- Security: [`../../../docs/08-security-threat-model.md`](../../../docs/08-security-threat-model.md) (only reversible actions may be speculated)

**Reversibility classes:** every tool is typed `idempotent`, `compensable`,
`snapshot-reversible`, or `irreversible`. Only the first three may ever be
speculated; irreversible actions require confirmation and never run on a speculative
branch.

**Core invariant (property-tested):** an aborted transaction leaves no observable
effect.

**Status:** scaffold — an in-memory effect/transaction model that holds the abort
invariant. Epoch frontiers and micro-VM snapshot reversibility are layered on later.
