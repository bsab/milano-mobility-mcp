from decimal import Decimal

import pytest
from pydantic import ValidationError

from milano_mobility_mcp.models import Decision, MoveInRequest
from milano_mobility_mcp.service import calculate_movein


def test_decimal_calculation_is_exact_and_never_authorizes():
    result = calculate_movein(MoveInRequest(
        km_percorsi="100.1", soglia_annuale="100.4", distanza_viaggio="0.2",
    ))
    assert result.km_residui == Decimal("0.3")
    assert result.km_residui_dopo_viaggio == Decimal("0.1")
    assert result.viaggio_nel_budget_dichiarato is True
    assert result.decision == Decision.UNKNOWN
    assert result.authenticated_balance is False
    assert result.input_provenance == "user_unverified"
    assert result.model_dump(mode="json")["km_residui"] == "0.3"


@pytest.mark.parametrize("driven,threshold,trip,remaining,overrun,fits,after_overrun", [
    (100, 100, 0, 0, 0, True, 0),
    (100, 100, 1, 0, 0, False, 1),
    (110, 100, 0, 0, 10, False, 10),
    (110, 100, 5, 0, 10, False, 15),
    (90, 100, 10, 10, 0, True, 0),
    (0, 0, 0, 0, 0, True, 0),
    (0, 0, 1, 0, 0, False, 1),
])
def test_budget_boundaries(driven, threshold, trip, remaining, overrun, fits, after_overrun):
    result = calculate_movein(MoveInRequest(
        km_percorsi=driven, soglia_annuale=threshold, distanza_viaggio=trip,
    ))
    assert result.km_residui == remaining
    assert result.km_eccedenti == overrun
    assert result.viaggio_nel_budget_dichiarato is fits
    assert result.km_eccedenti_dopo_viaggio == after_overrun
    assert result.km_residui_dopo_viaggio >= 0


@pytest.mark.parametrize("field", ["km_percorsi", "soglia_annuale", "distanza_viaggio"])
@pytest.mark.parametrize("invalid", [
    -1, "-0.000001", "NaN", "Infinity", "-Infinity", float("nan"), float("inf"),
    True, False, None, "abc", "1e1000", "1000000001", "0.0000001",
])
def test_rejects_invalid_distances(field, invalid):
    values = dict(km_percorsi=0, soglia_annuale=100, distanza_viaggio=1)
    values[field] = invalid
    with pytest.raises(ValidationError):
        MoveInRequest(**values)
