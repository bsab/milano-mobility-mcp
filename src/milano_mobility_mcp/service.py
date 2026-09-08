"""Valutazioni conservative, prive di rete e riproducibili con un clock esplicito."""

from collections.abc import Callable, Iterable
from datetime import UTC, datetime, time, timedelta
from decimal import Decimal

from .adapters import SmogAdapter
from .catalog import Snapshot, assess_source
from .models import (
    ROME, AccessRequest, AccessResult, Assessment, CostsRequest, CostsResult,
    Decision, Evidence, MoveInRequest, MoveInResult, SmogRequest, SmogResult, SourceCheck,
)


def aggregate_decisions(decisions: Iterable[Decision]) -> Decision:
    # Un divieto noto prevale sulle lacune; l'assenza di divieti non prova l'accesso.
    return Decision.DENIED if Decision.DENIED in decisions else Decision.UNKNOWN


def calculate_movein(
    request: MoveInRequest, source_checks: tuple[SourceCheck, ...] = (),
) -> MoveInResult:
    driven, threshold, trip = request.km_percorsi, request.soglia_annuale, request.distanza_viaggio
    zero = Decimal("0")
    return MoveInResult(
        km_percorsi=driven,
        soglia_annuale=threshold,
        distanza_viaggio=trip,
        km_residui=max(threshold - driven, zero),
        km_eccedenti=max(driven - threshold, zero),
        viaggio_nel_budget_dichiarato=driven + trip <= threshold,
        km_residui_dopo_viaggio=max(threshold - driven - trip, zero),
        km_eccedenti_dopo_viaggio=max(driven + trip - threshold, zero),
        source_checks=list(source_checks),
        reasons=[
            "Valori forniti dall'utente, non verificati; nessun saldo personale autenticato.",
            "Il calcolo non determina soglia spettante, rinnovo, arrotondamenti del servizio o deroghe.",
            "Un viaggio nel budget dichiarato NON autorizza ingresso o circolazione.",
        ],
    )


class MobilityService:
    def __init__(
        self,
        snapshot: Snapshot,
        smog_adapter: SmogAdapter,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.snapshot = snapshot
        self.smog_adapter = smog_adapter
        self.clock = clock or (lambda: datetime.now(ROME))

    def now(self) -> datetime:
        value = self.clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Il clock deve avere una timezone.")
        return value.astimezone(ROME)

    def get_active_smog_level(self, request: SmogRequest) -> SmogResult:
        return self.smog_adapter.read(request.territory, self.now())

    def check_vehicle_access(self, request: AccessRequest) -> AccessResult:
        now = self.now()
        at = request.at
        reasons = []
        can_apply = True
        if at.astimezone(UTC) > now.astimezone(UTC):
            can_apply = False
            reasons.append("Istante futuro: nessuna verifica prospettica delle restrizioni.")
        if not request.inside_area_confirmed_by_user:
            can_apply = False
            reasons.append("Appartenenza al perimetro non confermata; nessuna geocodifica disponibile.")
        if request.vehicle.exemptions != "nessuna_applicabile_dichiarata":
            can_apply = False
            reasons.append("Deroghe, accessi residui o adesione MoVe-In da verificare esternamente.")
        reasons.append("Profilo, residenza e assenza di deroghe sono dichiarazioni non verificate.")
        assessments = []
        for rule in self.snapshot.denials:
            if rule.area != request.area:
                continue
            evidence = assess_source(rule.id, rule.source, now, at.date())
            matches = (
                request.vehicle.category == rule.category
                and request.vehicle.fuel == rule.fuel
                and request.vehicle.euro_class in rule.euro_classes
                and at.date() in rule.service_dates
                and rule.starts_at <= at.time() < rule.ends_at
            )
            denied = can_apply and matches and evidence.freshness == "current"
            assessments.append(Assessment(
                scope=rule.id,
                decision=Decision.DENIED if denied else Decision.UNKNOWN,
                reasons=[
                    "Divieto ordinario documentato per questo profilo e orario, senza deroghe applicabili dichiarate."
                    if denied else
                    "Regola non applicabile o non verificabile: non equivale a veicolo ammesso."
                ],
                evidence=[evidence],
            ))
        assessments.append(Assessment(
            scope="copertura_complessiva",
            decision=Decision.UNKNOWN,
            reasons=[
                "Copertura parziale: deroghe, disponibilità di accessi, percorso e altre restrizioni non verificati.",
                "La residenza non garantisce esenzioni; fuori orario non viene emesso un via libera.",
            ],
            evidence=[Evidence(rule_id="copertura_completa", source=None, freshness="missing")],
        ))
        smog = self.smog_adapter.read("Comune di Milano", now)
        assessments.append(Assessment(
            scope="misure_temporanee_antismog",
            decision=smog.decision,
            reasons=smog.reasons,
        ))
        decision = aggregate_decisions(a.decision for a in assessments)
        reasons.append(
            "Un divieto ordinario documentato prevale sulle altre componenti sconosciute."
            if decision == Decision.DENIED else
            "Non ci sono prove sufficienti per determinare l'accesso; nessuna autorizzazione implicita."
        )
        return AccessResult(
            decision=decision,
            reasons=reasons,
            evaluated_at=now,
            requested_at_rome=at,
            area=request.area,
            assessments=assessments,
            source_checks=[check for check in self.snapshot.source_checks
                           if check.topic in (request.area.value, "smog")],
        )

    def get_daily_costs(self, request: CostsRequest) -> CostsResult:
        now = self.now()
        evidence = []
        source_checks = [check for check in self.snapshot.source_checks if check.topic == request.area.value]
        for rule in self.snapshot.tariffs:
            if rule.area != request.area:
                continue
            checked = assess_source(rule.id, rule.source, now, request.on_date)
            evidence.append(checked)
            if (checked.freshness == "current" and request.tariff == "ordinaria"
                    and request.on_date in rule.service_dates):
                deadline_day = request.on_date + timedelta(days=rule.activation_days_after_access + 1)
                return CostsResult(
                    calculation_status="documentato",
                    area=request.area,
                    on_date=request.on_date,
                    evaluated_at=now,
                    ordinary_ticket_eur=rule.amount_eur,
                    activation_deadline_exclusive=datetime.combine(deadline_day, time.min, ROME),
                    reasons=[
                        "Tariffa del ticket ordinario, NON importo personale dovuto né autorizzazione all'accesso.",
                        "Scadenza esclusiva: attivare prima dell'istante indicato (fine del giorno previsto dalla fonte).",
                        "Esenzioni, agevolazioni, sanzioni e altri costi non calcolati: totale dovuto sconosciuto.",
                    ],
                    evidence=evidence,
                    source_checks=source_checks,
                )
        return CostsResult(
            calculation_status="non_determinabile",
            area=request.area,
            on_date=request.on_date,
            evaluated_at=now,
            reasons=[
                "Nessuna tariffa e scadenza verificate per area, data e regime richiesti.",
                "Importi e scadenza null: sconosciuto non significa ticket gratuito o assenza di costi.",
            ],
            evidence=evidence or [Evidence(rule_id="tariffa_non_disponibile", source=None, freshness="missing")],
            source_checks=source_checks,
        )
