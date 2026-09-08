"""Regole versionate: nessun caricamento implicito di dati utente come fonti."""

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal

from .models import ROME, Area, Evidence, Source, SourceCheck


@dataclass(frozen=True)
class DenialRule:
    id: str
    area: Area
    category: str
    fuel: str
    euro_classes: tuple[int, ...]
    service_dates: tuple[date, ...]
    starts_at: time
    ends_at: time
    source: Source | None


@dataclass(frozen=True)
class TariffRule:
    id: str
    area: Area
    amount_eur: Decimal
    activation_days_after_access: int
    service_dates: tuple[date, ...]
    source: Source | None


@dataclass(frozen=True)
class Snapshot:
    denials: tuple[DenialRule, ...] = ()
    tariffs: tuple[TariffRule, ...] = ()
    source_checks: tuple[SourceCheck, ...] = ()


def assess_source(rule_id: str, source: Source | None, now: datetime, day: date) -> Evidence:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("La valutazione della fonte richiede un istante con timezone.")
    now = now.astimezone(ROME)
    if source is None:
        freshness = "missing"
    elif source.kind != "official_public":
        freshness = "unverified"
    elif now.astimezone(UTC) < source.checked_at.astimezone(UTC):
        freshness = "future_observation"
    elif now.astimezone(UTC) > min(
        source.fresh_until.astimezone(UTC), source.checked_at.astimezone(UTC) + timedelta(hours=24),
    ):
        freshness = "stale"
    elif (day > now.date() or not source.coverage_from <= day <= source.coverage_through
          or (source.legal_effective_from is not None and day < source.legal_effective_from)
          or (source.legal_effective_through is not None and day > source.legal_effective_through)):
        freshness = "outside_coverage"
    else:
        freshness = "current"
    return Evidence(rule_id=rule_id, source=source, freshness=freshness)
