"""Riferimenti consultati, NON prove di regole operative attualmente applicabili."""

from datetime import date

from .catalog import Snapshot
from .models import SourceCheck

CHECKED_ON = date(2026, 9, 8)

SOURCE_CHECKS = (
    SourceCheck(
        id="comune-area-b", topic="area_b", title="Area B",
        url="https://www.comune.milano.it/argomenti/mobilita/area-b",
        authority="Comune di Milano", checked_on=CHECKED_ON, retrieval="http_403",
        note="HTTP 403: condizioni, orari, deroghe e validità non verificati direttamente.",
    ),
    SourceCheck(
        id="comune-area-b-calendario", topic="area_b", title="Area B | Calendario dei divieti",
        url="https://www.comune.milano.it/argomenti/mobilita/area-b-calendario-dei-divieti",
        authority="Comune di Milano", checked_on=CHECKED_ON, retrieval="http_403",
        note="HTTP 403: nessuna data di servizio o classe vietata abilitata nel catalogo.",
    ),
    SourceCheck(
        id="comune-area-b-euro0", topic="area_b",
        title="Posso accedere ad Area B con un veicolo a benzina Euro 0?",
        url="https://servizicrm.comune.milano.it/centro-supporto/KA-01272/Accesso-Area-B-per-veicoli-benzina-Euro-",
        authority="Comune di Milano", checked_on=CHECKED_ON, retrieval="http_403",
        note="HTTP 403: il titolo e i risultati di ricerca non bastano per attivare un divieto.",
    ),
    SourceCheck(
        id="comune-area-c-ticket", topic="area_c", title="Come si acquistano i ticket Area C?",
        url="https://servizicrm.comune.milano.it/centro-supporto/KA-01154/Acquisto-ticket-Area-C",
        authority="Comune di Milano", checked_on=CHECKED_ON, retrieval="http_403",
        note="HTTP 403: tariffa e scadenza di attivazione non verificate per alcuna data.",
    ),
    SourceCheck(
        id="comune-area-c-pdf", topic="area_c", title="Area C nuove tariffe dal 2023 Area C.pdf",
        url="https://www.comune.milano.it/documents/20118/35188/Area+C+nuove+tariffe+dal+2023+Area+C.pdf/5ee21a73-7301-60c7-d2fe-5e2f77e8a158?version=1.0&t=1746021538283&download=true",
        authority="Comune di Milano", checked_on=CHECKED_ON, retrieval="pdf_not_verified",
        note="HTTP 200 PDF; contenuto non verificato nella ricerca. Nome file e disponibilità non provano vigenza nel 2026.",
    ),
    SourceCheck(
        id="regione-misure-temporanee", topic="smog",
        title="Misure temporanee per migliorare la qualità dell'aria",
        url="https://www.regione.lombardia.it/ambiente-e-territorio/qualita-dell-aria/red-misure-temporanee-per-miglioramento-qualita-aria",
        authority="Regione Lombardia", checked_on=CHECKED_ON, retrieval="readable",
        page_updated_on=date(2026, 7, 16),
        note="Pagina informativa: indica InfoAria per misure e notifiche di attivazione; non è un bollettino territoriale attivo.",
    ),
    SourceCheck(
        id="regione-infoaria", topic="smog", title="Info Aria",
        url="https://www.infoaria.regione.lombardia.it/infoaria/#/home",
        authority="Regione Lombardia", checked_on=CHECKED_ON, retrieval="javascript_shell",
        note="HTTP 200, sola shell JavaScript: nessun livello, territorio o periodo ufficiale acquisito.",
    ),
    SourceCheck(
        id="arpa-aria", topic="smog", title="ARPA Lombardia | Aria",
        url="https://www.arpalombardia.it/temi-ambientali/aria/",
        authority="ARPA Lombardia", checked_on=CHECKED_ON, retrieval="readable",
        page_updated_on=date(2025, 9, 9),
        note="Descrive misurazioni della rete e stime modellistiche, non prova di attivazione/revoca dei provvedimenti.",
    ),
    SourceCheck(
        id="regione-movein", topic="movein", title="Servizio MoVe-In",
        url="https://www.regione.lombardia.it/ambiente-e-territorio/qualita-dell-aria/servizio-move-in",
        authority="Regione Lombardia", checked_on=CHECKED_ON, retrieval="readable",
        page_updated_on=date(2026, 5, 21),
        note=(
            "La limitazione chilometrica non si applica quando sono attive misure temporanee. "
            "MoVe-In non autorizza le ZTL comunali salvo estensione comunale; Area B è un esempio. "
            "Area C non è nominata esplicitamente nel testo verificato. Nessun saldo personale acquisito."
        ),
    ),
)

SMOG_SOURCE_CHECKS = tuple(check for check in SOURCE_CHECKS if check.topic == "smog")
SMOG_REFERENCE_URLS = tuple(check.url for check in SMOG_SOURCE_CHECKS)
MOVEIN_SOURCE_CHECKS = tuple(check for check in SOURCE_CHECKS if check.topic == "movein")

# La consultazione di pagine pubbliche non basta a dimostrare una regola eseguibile.
PUBLIC_SNAPSHOT = Snapshot(source_checks=SOURCE_CHECKS)
