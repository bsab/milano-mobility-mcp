"""Adapter esplicito per uno stato ufficiale non disponibile nel MVP."""

from datetime import datetime
from typing import Protocol

from .models import SmogResult, SourceCheck


class SmogAdapter(Protocol):
    def read(self, territory: str, now: datetime) -> SmogResult: ...


class UnavailableSmogAdapter:
    def __init__(
        self, reference_urls: tuple[str, ...], source_checks: tuple[SourceCheck, ...] = (),
    ) -> None:
        self.reference_urls = reference_urls
        self.source_checks = source_checks

    def read(self, territory: str, now: datetime) -> SmogResult:
        return SmogResult(
            requested_territory=territory,
            authority="Regione Lombardia / autorità competente per il territorio e il provvedimento",
            evaluated_at=now,
            reasons=[
                "Nessun bollettino ufficiale attivo acquisito per territorio e periodo richiesti.",
                "L'adapter non interroga una API live: livello, validità e last_checked restano null.",
                "Le misurazioni ARPA non sono una prova dell'attivazione o revoca di misure.",
                "Stato sconosciuto non significa livello zero o assenza di restrizioni.",
            ],
            reference_urls=list(self.reference_urls),
            source_checks=list(self.source_checks),
        )
