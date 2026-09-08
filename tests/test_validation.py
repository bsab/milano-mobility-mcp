from datetime import datetime

import pytest
from pydantic import ValidationError

from milano_mobility_mcp.models import AccessRequest, CostsRequest, SmogRequest, Vehicle


def access_payload(at):
    return dict(
        vehicle=dict(category="M1", fuel="benzina", euro_class=0,
                     exemptions="nessuna_applicabile_dichiarata"),
        at=at, area="area_b", inside_area_confirmed_by_user=True,
    )


@pytest.mark.parametrize("at", [
    "2026-09-08T12:00:00", "2026-09-08", "2026-09-08T12:00:00Z",
    "2026-09-08T12:00:00+01:00", "2026-03-29T02:30:00+01:00",
    "2026-03-29T02:30:00+02:00", 1788868800, True,
])
def test_rejects_naive_wrong_offset_and_nonexistent_rome_times(at):
    with pytest.raises(ValidationError):
        AccessRequest(**access_payload(at))


@pytest.mark.parametrize("at", [
    "2026-09-08T12:00:00+02:00", "2026-01-08T12:00:00+01:00",
    "2026-10-25T02:30:00+02:00", "2026-10-25T02:30:00+01:00",
])
def test_accepts_rome_offsets_including_both_autumn_folds(at):
    parsed = AccessRequest(**access_payload(at)).at
    assert str(parsed.tzinfo) == "Europe/Rome"
    assert parsed.utcoffset() == datetime.fromisoformat(at).utcoffset()


def test_explicit_vehicle_profile_and_no_extra_personal_data():
    with pytest.raises(ValidationError):
        Vehicle(category="M1", fuel="benzina", euro_class=None,
                exemptions="nessuna_applicabile_dichiarata")
    values = access_payload("2026-09-08T12:00:00+02:00")
    values["plate"] = "not-an-accepted-input"
    with pytest.raises(ValidationError):
        AccessRequest(**values)
    values.pop("plate")
    values["inside_area_confirmed_by_user"] = "false"
    with pytest.raises(ValidationError):
        AccessRequest(**values)


@pytest.mark.parametrize("day", ["2026-09-08T00:00:00", "20260908", True, 1788868800])
def test_costs_requires_calendar_date(day):
    with pytest.raises(ValidationError):
        CostsRequest(area="area_c", on_date=day, tariff="ordinaria")


@pytest.mark.parametrize("territory", ["", " ", "x", "a" * 121])
def test_smog_requires_explicit_territory(territory):
    with pytest.raises(ValidationError):
        SmogRequest(territory=territory)
