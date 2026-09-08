"""Contratti di input/output e provenienza delle informazioni."""

from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal
from zoneinfo import ZoneInfo

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

ROME = ZoneInfo("Europe/Rome")


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Decision(StrEnum):
    ALLOWED = "consentito"
    DENIED = "vietato"
    UNKNOWN = "non_determinabile"


class Area(StrEnum):
    B = "area_b"
    C = "area_c"


class Vehicle(Model):
    category: Literal["M1", "M2", "M3", "N1", "N2", "N3", "L", "altro"]
    fuel: Literal[
        "benzina", "diesel", "elettrico", "ibrido_benzina", "ibrido_diesel",
        "gpl", "metano", "altro",
    ]
    euro_class: Annotated[int, Field(strict=True, ge=0, le=6)] | None
    exemptions: Literal["nessuna_applicabile_dichiarata", "da_verificare"]
    resident_in_milan: Annotated[bool, Field(strict=True)] | None = None

    @model_validator(mode="after")
    def require_euro_class(self) -> "Vehicle":
        if self.fuel != "elettrico" and self.euro_class is None:
            raise ValueError("Specificare la classe Euro per un veicolo non elettrico.")
        return self


class AccessRequest(Model):
    vehicle: Vehicle
    at: AwareDatetime
    area: Area
    inside_area_confirmed_by_user: Annotated[bool, Field(strict=True)]
    destination: Annotated[str, Field(min_length=1, max_length=200)] | None = None

    @field_validator("at", mode="before")
    @classmethod
    def require_datetime(cls, value: object) -> object:
        if not isinstance(value, (str, datetime)):
            raise ValueError("Usare una data/ora ISO 8601 con offset di Europe/Rome.")
        return value

    @field_validator("at")
    @classmethod
    def validate_rome_time(cls, value: datetime) -> datetime:
        local = value.astimezone(ROME)
        if value.utcoffset() != local.utcoffset():
            raise ValueError("L'offset deve corrispondere a Europe/Rome in quell'istante.")
        return local


Kilometres = Annotated[Decimal, Field(ge=0, le=1_000_000_000, max_digits=16, decimal_places=6)]


class MoveInRequest(Model):
    km_percorsi: Kilometres
    soglia_annuale: Kilometres
    distanza_viaggio: Kilometres

    @field_validator("km_percorsi", "soglia_annuale", "distanza_viaggio", mode="before")
    @classmethod
    def reject_boolean(cls, value: object) -> object:
        if isinstance(value, bool):
            raise ValueError("Un booleano non è una distanza.")
        return value


class CostsRequest(Model):
    area: Area
    on_date: date
    tariff: Literal["ordinaria", "agevolata", "sconosciuta"]

    @field_validator("on_date", mode="before")
    @classmethod
    def require_calendar_date(cls, value: object) -> object:
        if isinstance(value, datetime) or not isinstance(value, (str, date)):
            raise ValueError("Usare una data di calendario YYYY-MM-DD.")
        if isinstance(value, str):
            try:
                parsed = date.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("Usare una data di calendario YYYY-MM-DD.") from exc
            if parsed.isoformat() != value:
                raise ValueError("Usare una data di calendario YYYY-MM-DD.")
        return value


class SmogRequest(Model):
    territory: Annotated[str, Field(min_length=2, max_length=120)]

    @field_validator("territory")
    @classmethod
    def strip_territory(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Specificare un territorio.")
        return value


class Source(Model):
    id: str
    title: str
    url: str
    authority: str
    kind: Literal["official_public", "user_unverified", "synthetic_test"]
    checked_at: AwareDatetime
    fresh_until: AwareDatetime
    coverage_from: date
    coverage_through: date
    legal_effective_from: date | None = None
    legal_effective_through: date | None = None
    excerpt: str
    limitations: list[str]

    @model_validator(mode="after")
    def ordered_periods(self) -> "Source":
        if self.fresh_until.astimezone(UTC) < self.checked_at.astimezone(UTC):
            raise ValueError("Freschezza antecedente alla consultazione.")
        if self.coverage_through < self.coverage_from:
            raise ValueError("Copertura temporale invertita.")
        if (self.legal_effective_from and self.legal_effective_through
                and self.legal_effective_through < self.legal_effective_from):
            raise ValueError("Periodo normativo invertito.")
        return self


class SourceCheck(Model):
    id: str
    topic: Literal["area_b", "area_c", "smog", "movein"]
    title: str
    url: str
    authority: str
    checked_on: date
    retrieval: Literal["readable", "http_403", "javascript_shell", "pdf_not_verified"]
    page_updated_on: date | None = None
    legal_valid_from: date | None = None
    legal_valid_through: date | None = None
    rule_validity: Literal["non_verificata"] = "non_verificata"
    freshness: Literal["reference_only"] = "reference_only"
    note: str


class Evidence(Model):
    rule_id: str
    source: Source | None
    freshness: Literal[
        "current", "missing", "stale", "future_observation", "outside_coverage", "unverified",
    ]


class Assessment(Model):
    scope: str
    decision: Decision
    reasons: list[str]
    evidence: list[Evidence] = Field(default_factory=list)


class AccessResult(Model):
    decision: Decision
    reasons: list[str]
    evaluated_at: AwareDatetime
    requested_at_rome: AwareDatetime
    area: Area
    input_provenance: Literal["user_unverified"] = "user_unverified"
    decision_scope: str = "Regime ordinario sul profilo e sul perimetro dichiarati; non autorizzazione."
    assessments: list[Assessment]
    source_checks: list[SourceCheck] = Field(default_factory=list)
    geographic_limitations: str = (
        "Nessuna geocodifica, verifica civico, percorso, confine o varco. "
        "L'appartenenza all'area è dichiarata dall'utente, non verificata."
    )


class SmogResult(Model):
    decision: Decision = Decision.UNKNOWN
    requested_territory: str
    authoritative_territory: str | None = None
    active_level: int | None = None
    authority: str
    authority_status: Literal["non_verificato"] = "non_verificato"
    valid_from: AwareDatetime | None = None
    valid_until: AwareDatetime | None = None
    last_checked: AwareDatetime | None = None
    evaluated_at: AwareDatetime
    reasons: list[str]
    reference_urls: list[str]
    source_checks: list[SourceCheck] = Field(default_factory=list)
    freshness: Literal["missing"] = "missing"


class MoveInResult(Model):
    decision: Decision = Decision.UNKNOWN
    calculation_status: Literal["calcolato"] = "calcolato"
    input_provenance: Literal["user_unverified"] = "user_unverified"
    km_percorsi: Decimal
    soglia_annuale: Decimal
    distanza_viaggio: Decimal
    km_residui: Decimal
    km_eccedenti: Decimal
    viaggio_nel_budget_dichiarato: bool
    km_residui_dopo_viaggio: Decimal
    km_eccedenti_dopo_viaggio: Decimal
    authenticated_balance: Literal[False] = False
    source_checks: list[SourceCheck] = Field(default_factory=list)
    rule: str = "Sola sottrazione e confronto sui tre valori dichiarati; nessuna formula normativa."
    reasons: list[str]


class CostsResult(Model):
    decision: Decision = Decision.UNKNOWN
    calculation_status: Literal["documentato", "non_determinabile"]
    area: Area
    on_date: date
    evaluated_at: AwareDatetime
    ordinary_ticket_eur: Decimal | None = None
    total_due_eur: Decimal | None = None
    activation_deadline_exclusive: AwareDatetime | None = None
    currency: Literal["EUR"] = "EUR"
    reasons: list[str]
    evidence: list[Evidence]
    source_checks: list[SourceCheck] = Field(default_factory=list)
