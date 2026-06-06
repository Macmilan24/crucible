from __future__ import annotations

from crucible_bench import ArmResult, RunManifest, passes_phase0_gate


def _stock() -> ArmResult:
    return ArmResult("stock", mean_tokens=40_000, malformed_rate=0.05, success_rate=0.50)


def test_gate_passes_on_big_saving_at_matched_success() -> None:
    crucible = ArmResult("crucible", mean_tokens=5_000, malformed_rate=0.0, success_rate=0.50)
    result = passes_phase0_gate(_stock(), crucible)
    assert result.passed
    assert result.reduction_factor == 8.0


def test_gate_fails_below_2x() -> None:
    crucible = ArmResult("crucible", mean_tokens=30_000, malformed_rate=0.0, success_rate=0.50)
    result = passes_phase0_gate(_stock(), crucible)
    assert not result.passed
    assert "< required" in result.reason


def test_gate_fails_if_success_regressed() -> None:
    # Huge token saving, but success collapsed → not a real win.
    crucible = ArmResult("crucible", mean_tokens=2_000, malformed_rate=0.0, success_rate=0.30)
    result = passes_phase0_gate(_stock(), crucible)
    assert not result.passed
    assert "success regressed" in result.reason


def test_manifest_reproducibility_check() -> None:
    good = RunManifest(
        commit="abc123",
        suite="SWE-rebench",
        model="qwen2.5-7b",
        model_hash="sha256:...",
        seeds=(1, 2, 3),
        hardware="M3/24GB",
        env_lock_hash="sha256:lock",
    )
    assert good.is_reproducible()

    bad = RunManifest(
        commit="",
        suite="SWE-rebench",
        model="qwen2.5-7b",
        model_hash="sha256:...",
        seeds=(),
        hardware="M3/24GB",
        env_lock_hash="",
    )
    assert not bad.is_reproducible()
