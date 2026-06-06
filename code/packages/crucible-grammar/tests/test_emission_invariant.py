"""The core invariant, as a property test:

    Every token the masked decoder can emit is accepted by the active schema.

This is the structural-hallucination-is-impossible guarantee, tested over many
generated vocabularies and schemas rather than a handful of examples.
"""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from crucible_engine import ROOT, MockEngine
from crucible_grammar import EmissionSchema, Phase, mask_for_phase


@given(
    vocab_size=st.integers(min_value=1, max_value=64),
    allowed=st.sets(st.integers(min_value=0, max_value=63), min_size=1),
)
def test_masked_emission_is_always_schema_valid(vocab_size: int, allowed: set[int]) -> None:
    allowed_in_vocab = frozenset(t for t in allowed if t < vocab_size)
    if not allowed_in_vocab:
        return  # no representable allowed token for this vocab; nothing to assert
    schema = EmissionSchema(allowed_in_vocab)
    mask = schema.mask(vocab_size)

    # Invariant 1: the mask permits exactly the schema's tokens.
    for tok in range(vocab_size):
        assert mask[tok] == schema.accepts(tok)

    # Invariant 2: a token sampled under the mask is always schema-valid.
    eng = MockEngine(vocab_size=vocab_size)
    sampled = eng.sample(ROOT, mask=mask)
    assert schema.accepts(sampled)


def test_cognition_is_never_masked() -> None:
    schema = EmissionSchema(frozenset({1}))
    assert mask_for_phase(Phase.THINK, schema, vocab_size=4) is None
    assert mask_for_phase(Phase.REFLECT, schema, vocab_size=4) is None
    # ...but emission is.
    assert mask_for_phase(Phase.EMIT, schema, vocab_size=4) == [False, True, False, False]
