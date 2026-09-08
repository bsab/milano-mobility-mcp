"""Scenari sintetici locali: non sono regole/fonti distribuite nel package."""

from dataclasses import replace
from datetime import date, datetime, time, timedelta
from decimal import Decimal

import pytest

from milano_mobility_mcp.adapters import UnavailableSmogAdapter
from milano_mobility_mcp.catalog import DenialRule, Snapshot, TariffRule
from milano_mobility_mcp.models import (
    ROME, AccessRequest, Area, CostsRequest, Decision, SmogRequest, Source,
)
from milano_mobility_mcp.service import MobilityService, aggregate_decisions

DAY = date(2026, 9, 8)
NOW = datetime(2026, 9, 8, 20, tzinfo=ROME)


@pytest.fixture
def snapshot():
    source = Source(
        id="test-only", title="Synthetic source contract", authority="Test only",
        url="https://example.invalid/test", kind="official_public",
        checked_at=datetime(2026, 9, 8, 12, tzinfo=ROME),
        fresh_until=datetime(2026, 9, 9, 12, tzinfo=ROME),
        coverage_from=DAY, coverage_through=DAY,
        excerpt="Synthetic test rule; not a real normative claim.", limitations=["Tests only"],
    )
    return Snapshot(
        denials=(DenialRule("test-denial", Area.B, "M1", "benzina", (0,), (DAY,),
                            time(7, 30), time(19, 30), source),),
        tariffs=(TariffRule("test-tariff", Area.C, Decimal("12.34"), 1, (DAY,), source),),
    )


def make_service(snapshot, now=NOW):
    return MobilityService(snapshot, UnavailableSmogAdapter(()), lambda: now)


def access(at="2026-09-08T12:00:00+02:00", **changes):
    values = dict(
        vehicle=dict(category="M1", fuel="benzina", euro_class=0,
                     exemptions="nessuna_applicabile_dichiarata"),
        at=at, area="area_b", inside_area_confirmed_by_user=True,
    )
    values.update(changes)
    return AccessRequest(**values)


@pytest.mark.parametrize("at,expected", [
    ("2026-09-08T07:29:59+02:00", Decision.UNKNOWN),
    ("2026-09-08T07:30:00+02:00", Decision.DENIED),
    ("2026-09-08T19:29:59+02:00", Decision.DENIED),
    ("2026-09-08T19:30:00+02:00", Decision.UNKNOWN),
    ("2026-09-08T22:00:00+02:00", Decision.UNKNOWN),
    ("2026-09-07T12:00:00+02:00", Decision.UNKNOWN),
    ("2026-09-09T12:00:00+02:00", Decision.UNKNOWN),
    ("2026-09-06T12:00:00+02:00", Decision.UNKNOWN),
])
def test_temporal_boundaries(snapshot, at, expected):
    assert make_service(snapshot).check_vehicle_access(access(at)).decision == expected


def test_future_instant_inside_service_hours_stays_unknown(snapshot):
    result = make_service(snapshot, datetime(2026, 9, 8, 12, tzinfo=ROME)).check_vehicle_access(
        access("2026-09-08T12:00:01+02:00"))
    assert result.decision == Decision.UNKNOWN
    assert any("futuro" in reason for reason in result.reasons)


def test_smog_unknown_does_not_hide_a_documented_denial(snapshot):
    result = make_service(snapshot).check_vehicle_access(access())
    assert result.decision == Decision.DENIED
    assert {a.decision for a in result.assessments} == {Decision.DENIED, Decision.UNKNOWN}
    assert all(a.decision != Decision.ALLOWED for a in result.assessments)


@pytest.mark.parametrize("decisions", [[], [Decision.UNKNOWN], [Decision.ALLOWED],
                                        [Decision.ALLOWED, Decision.UNKNOWN]])
def test_partial_coverage_never_allows(decisions):
    assert aggregate_decisions(decisions) == Decision.UNKNOWN


def test_missing_catalog_is_unknown_not_free(snapshot):
    service = make_service(Snapshot())
    assert service.check_vehicle_access(access()).decision == Decision.UNKNOWN
    result = service.get_daily_costs(CostsRequest(area="area_c", on_date=DAY, tariff="ordinaria"))
    assert result.ordinary_ticket_eur is None
    assert result.activation_deadline_exclusive is None
    assert result.total_due_eur is None


@pytest.mark.parametrize("kind", ["missing", "synthetic_test", "user_unverified", "stale"])
def test_unusable_evidence_cannot_determine_access_or_costs(snapshot, kind):
    source = snapshot.denials[0].source
    if kind == "missing":
        source = None
    elif kind == "stale":
        source = source.model_copy(update={"fresh_until": NOW - timedelta(seconds=1)})
    else:
        source = source.model_copy(update={"kind": kind})
    changed = Snapshot(
        denials=(replace(snapshot.denials[0], source=source),),
        tariffs=(replace(snapshot.tariffs[0], source=source),),
    )
    service = make_service(changed)
    assert service.check_vehicle_access(access()).decision == Decision.UNKNOWN
    costs = service.get_daily_costs(CostsRequest(area="area_c", on_date=DAY, tariff="ordinaria"))
    assert costs.calculation_status == "non_determinabile"
    assert costs.ordinary_ticket_eur is None
    assert costs.total_due_eur is None


@pytest.mark.parametrize("vehicle_change", [
    {"category": "N1"}, {"fuel": "diesel"}, {"euro_class": 1},
    {"exemptions": "da_verificare", "resident_in_milan": True},
])
def test_unsupported_profile_or_possible_exemptions_is_unknown(snapshot, vehicle_change):
    request = access()
    vehicle = request.vehicle.model_dump() | vehicle_change
    result = make_service(snapshot).check_vehicle_access(access(vehicle=vehicle))
    assert result.decision == Decision.UNKNOWN


def test_residence_alone_is_not_an_exemption(snapshot):
    vehicle = access().vehicle.model_dump() | {"resident_in_milan": True}
    assert make_service(snapshot).check_vehicle_access(access(vehicle=vehicle)).decision == Decision.DENIED


def test_unknown_geography_cannot_match_area_denial(snapshot):
    result = make_service(snapshot).check_vehicle_access(access(inside_area_confirmed_by_user=False))
    assert result.decision == Decision.UNKNOWN


def test_documented_list_price_is_not_total_due_or_access_permission(snapshot):
    result = make_service(snapshot).get_daily_costs(CostsRequest(
        area="area_c", on_date=DAY, tariff="ordinaria",
    ))
    assert result.calculation_status == "documentato"
    assert result.ordinary_ticket_eur == Decimal("12.34")
    assert result.total_due_eur is None
    assert result.decision == Decision.UNKNOWN
    assert result.activation_deadline_exclusive == datetime(2026, 9, 10, tzinfo=ROME)


@pytest.mark.parametrize("changes", [
    {"on_date": date(2026, 9, 9)}, {"on_date": date(2026, 9, 7)},
    {"area": "area_b"}, {"tariff": "agevolata"}, {"tariff": "sconosciuta"},
])
def test_uncovered_costs_remain_null(snapshot, changes):
    request = CostsRequest(**(dict(area="area_c", on_date=DAY, tariff="ordinaria") | changes))
    result = make_service(snapshot).get_daily_costs(request)
    assert result.calculation_status == "non_determinabile"
    assert result.ordinary_ticket_eur is None
    assert result.total_due_eur is None
    assert result.activation_deadline_exclusive is None


def test_service_day_allowlist_cannot_be_inferred_from_weekdays(snapshot):
    snapshot = Snapshot(
        denials=(replace(snapshot.denials[0], service_dates=()),),
        tariffs=(replace(snapshot.tariffs[0], service_dates=()),),
    )
    service = make_service(snapshot)
    assert service.check_vehicle_access(access()).decision == Decision.UNKNOWN
    assert service.get_daily_costs(CostsRequest(
        area="area_c", on_date=DAY, tariff="ordinaria",
    )).ordinary_ticket_eur is None


def test_smog_preserves_authority_and_temporal_unknowns(snapshot):
    result = make_service(snapshot).get_active_smog_level(SmogRequest(territory="  Milano  "))
    assert result.requested_territory == "Milano"
    assert result.authoritative_territory is None
    assert result.active_level is None
    assert result.last_checked is None
    assert result.valid_from is None and result.valid_until is None
    assert result.freshness == "missing"
    assert result.evaluated_at == NOW


def test_naive_clock_is_rejected(snapshot):
    with pytest.raises(ValueError, match="timezone"):
        make_service(snapshot, datetime(2026, 9, 8)).check_vehicle_access(access())
