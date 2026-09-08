"""Il package distribuito non deve promuovere riferimenti o fixture a regole reali."""

from datetime import datetime
from decimal import Decimal

import pytest

from milano_mobility_mcp.adapters import UnavailableSmogAdapter
from milano_mobility_mcp.models import ROME, AccessRequest, CostsRequest, Decision, MoveInRequest
from milano_mobility_mcp.service import MobilityService, calculate_movein
from milano_mobility_mcp.sources import (
    CHECKED_ON, MOVEIN_SOURCE_CHECKS, PUBLIC_SNAPSHOT, SMOG_REFERENCE_URLS,
    SMOG_SOURCE_CHECKS, SOURCE_CHECKS,
)


def test_release_contains_no_unverified_normative_rule_or_test_data():
    assert PUBLIC_SNAPSHOT.denials == ()
    assert PUBLIC_SNAPSHOT.tariffs == ()
    assert len(SOURCE_CHECKS) == 9
    assert all(check.checked_on == CHECKED_ON for check in SOURCE_CHECKS)
    assert all(check.freshness == "reference_only" for check in SOURCE_CHECKS)
    assert all(check.rule_validity == "non_verificata" for check in SOURCE_CHECKS)
    assert all(check.legal_valid_from is None and check.legal_valid_through is None
               for check in SOURCE_CHECKS)
    assert all("example.invalid" not in check.url for check in SOURCE_CHECKS)
    assert all(check.url.startswith("https://") for check in SOURCE_CHECKS)


@pytest.mark.parametrize("area", ["area_b", "area_c"])
def test_real_catalog_returns_honest_access_and_cost_unknowns(area):
    service = MobilityService(
        PUBLIC_SNAPSHOT, UnavailableSmogAdapter(SMOG_REFERENCE_URLS, SMOG_SOURCE_CHECKS),
        lambda: datetime(2026, 9, 8, 20, tzinfo=ROME),
    )
    result = service.check_vehicle_access(AccessRequest(
        vehicle=dict(category="M1", fuel="benzina", euro_class=0,
                     exemptions="nessuna_applicabile_dichiarata"),
        at="2026-09-08T12:00:00+02:00", area=area, inside_area_confirmed_by_user=True,
    ))
    assert result.decision == Decision.UNKNOWN
    assert any(check.retrieval == "http_403" for check in result.source_checks)
    assert any(e.freshness == "missing" for a in result.assessments for e in a.evidence)
    costs = service.get_daily_costs(CostsRequest(area=area, on_date=CHECKED_ON, tariff="ordinaria"))
    assert costs.ordinary_ticket_eur is None
    assert costs.activation_deadline_exclusive is None
    assert costs.total_due_eur is None
    assert costs.evidence[0].freshness == "missing"
    assert costs.source_checks


def test_movein_reference_is_context_not_calculation_input_or_permission():
    result = calculate_movein(MoveInRequest(
        km_percorsi="100.1", soglia_annuale="100.4", distanza_viaggio="0.2",
    ), MOVEIN_SOURCE_CHECKS)
    assert result.km_residui == Decimal("0.3")
    assert result.source_checks[0].id == "regione-movein"
    assert result.source_checks[0].rule_validity == "non_verificata"
    assert result.decision == Decision.UNKNOWN
