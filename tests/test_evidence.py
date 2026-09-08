"""Metadati sintetici confinati ai test; nessuna fixture viene caricata dal server."""

from datetime import date, datetime, timedelta

import pytest
from pydantic import ValidationError

from milano_mobility_mcp.catalog import assess_source
from milano_mobility_mcp.models import ROME, Source


@pytest.fixture
def source():
    # Simula un record ufficiale per testare il gate, non una fonte normativa reale.
    checked = datetime(2026, 9, 8, 12, tzinfo=ROME)
    return Source(
        id="test-only", title="Test only", url="https://example.invalid/test-only",
        authority="Synthetic authority for unit tests", kind="official_public",
        checked_at=checked, fresh_until=checked + timedelta(hours=24),
        coverage_from=date(2026, 9, 8), coverage_through=date(2026, 9, 8),
        excerpt="Synthetic test fixture, not a legal rule.", limitations=["Test only"],
    )


def test_missing_source():
    assert assess_source("missing", None, datetime(2026, 9, 8, 13, tzinfo=ROME),
                         date(2026, 9, 8)).freshness == "missing"


@pytest.mark.parametrize("kind", ["synthetic_test", "user_unverified"])
def test_unverified_source_never_becomes_official(source, kind):
    unverified = source.model_copy(update={"kind": kind})
    assert assess_source("test", unverified, source.checked_at,
                         source.coverage_from).freshness == "unverified"


def test_freshness_boundaries(source):
    day = source.coverage_from
    assert assess_source("test", source, source.checked_at, day).freshness == "current"
    assert assess_source("test", source, source.fresh_until, day).freshness == "current"
    assert assess_source("test", source, source.fresh_until + timedelta(microseconds=1),
                         day).freshness == "stale"
    assert assess_source("test", source, source.checked_at - timedelta(microseconds=1),
                         day).freshness == "future_observation"


@pytest.mark.parametrize("offset", [-1, 1])
def test_outside_verified_coverage(source, offset):
    day = source.coverage_from + timedelta(days=offset)
    assert assess_source("test", source, source.checked_at, day).freshness == "outside_coverage"


def test_maximum_freshness_cannot_be_extended_by_a_record(source):
    extended = source.model_copy(update={"fresh_until": source.checked_at + timedelta(days=30)})
    now = source.checked_at + timedelta(hours=24, microseconds=1)
    assert assess_source("test", extended, now, source.coverage_from).freshness == "stale"


def test_legal_period_is_an_additional_constraint(source):
    tomorrow = source.coverage_from + timedelta(days=1)
    not_yet_effective = source.model_copy(update={"legal_effective_from": tomorrow})
    assert assess_source("test", not_yet_effective, source.checked_at,
                         source.coverage_from).freshness == "outside_coverage"
    expired = source.model_copy(update={"legal_effective_through": source.coverage_from - timedelta(days=1)})
    assert assess_source("test", expired, source.checked_at,
                         source.coverage_from).freshness == "outside_coverage"


@pytest.mark.parametrize("change", [
    {"coverage_through": date(2026, 9, 7)},
    {"fresh_until": datetime(2026, 9, 8, 11, tzinfo=ROME)},
    {"legal_effective_from": date(2026, 9, 9), "legal_effective_through": date(2026, 9, 8)},
])
def test_rejects_inverted_periods(source, change):
    with pytest.raises(ValidationError):
        Source.model_validate(source.model_dump() | change)
