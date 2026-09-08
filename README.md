# Milano Mobility MCP

MVP Python funzionante del **Nodo Mobilità & Restrizioni**: quattro tool MCP stdio per ridurre l'asimmetria informativa su Area B, Area C, MoVe-In e antismog a Milano. Urbanistica esclusa.

**Non è un'autorizzazione alla circolazione né consulenza legale.** Verificare sempre le disposizioni delle autorità e la propria situazione prima di viaggiare. Nessuna garanzia contro sanzioni.

## Cosa funziona davvero

| Tool | Supporto nel MVP |
|---|---|
| `check_vehicle_access` | Profilo, data e perimetro validati; **attualmente sempre `non_determinabile`**, con motivazioni e riferimenti. Nessun divieto abilitato: fonti comunali non verificabili nella consultazione. |
| `get_active_smog_level` | Adapter **non live**: livello, territorio del provvedimento, validità e ultima verifica sconosciuti. Riferimenti ufficiali per verifica esterna. |
| `query_movein_allowance` | Calcolo esatto `Decimal` sui tre valori dichiarati dall'utente. Non legge il saldo personale né determina la soglia normativa. |
| `get_daily_costs` | **Attualmente sempre `non_determinabile`**: tariffa, totale e scadenza `null`, **non zero**. Nessuna tariffa verificata vigente e quindi nessuna abilitata. |

SDK ufficiale [`mcp`](https://github.com/modelcontextprotocol/python-sdk), modelli Pydantic, Python **3.11+**. Nessuna richiesta di rete effettuata dai tool. Risposte con `structuredContent` e contenuto JSON testuale MCP.

### Esiti e prove

- `decision`: `consentito`, `vietato`, `non_determinabile`. **Questa versione non emette mai `consentito`**: la copertura complessiva è incompleta.
- Il motore supporta `vietato` per un divieto ordinario documentato sul profilo dichiarato, condizionato all'assenza di deroghe applicabili dichiarata dall'utente. **Questo ramo è esercitato da fixture sintetiche nei test, non da regole distribuite nel catalogo attuale.**
- Un divieto verificato prevale su componenti sconosciute, tutte visibili in `assessments`.
- Per budget/costi, `decision` resta `non_determinabile` rispetto alla circolazione; `calculation_status` distingue `calcolato`, `documentato`, `non_determinabile`.
- Input: `user_unverified`. Il motore richiede `official_public` per fonti operative; record `synthetic_test` o non verificati non sostengono regole. I `source_checks` restituiti sono riferimenti documentali (`reference_only`), **non prove di regole applicabili**.
- Fonti mancanti, scadute, consultate nel futuro o fuori copertura non producono divieti documentati, costi certi o autorizzazioni. Sconosciuto **non** significa nessun blocco, ticket gratuito o deroga garantita.

## Quickstart

Accesso al repository privato necessario. Nessun token applicativo, account MoVe-In o credenziale da inserire nel progetto.

### Windows / PowerShell

```powershell
gh repo clone bsab/milano-mobility-mcp
Set-Location milano-mobility-mcp
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[test]'
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m milano_mobility_mcp
```

Entry point alternativo: `.\.venv\Scripts\milano-mobility-mcp.exe`.

### Linux / macOS

```bash
gh repo clone bsab/milano-mobility-mcp
cd milano-mobility-mcp
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m pytest -q
.venv/bin/python -m milano_mobility_mcp
```

Entry point alternativo: `.venv/bin/milano-mobility-mcp`.

Il processo attende messaggi MCP su stdin: **non è una REPL né un server HTTP**. Nessun banner su stdout; arresto manuale con Ctrl+C. Normalmente lo avvia il client MCP. Installazione senza pytest: `pip install -e .` con l'interprete dell'ambiente.

## Configurazione client MCP

Usare l'interprete **assoluto del virtualenv**, non `python` dipendente dal PATH. Sostituire il percorso d'esempio con quello reale. Il package installato non dipende dalla directory corrente del client.

Windows:

```json
{
  "mcpServers": {
    "milano-mobility": {
      "command": "C:\\progetti\\milano-mobility-mcp\\.venv\\Scripts\\python.exe",
      "args": ["-m", "milano_mobility_mcp"]
    }
  }
}
```

Linux/macOS:

```json
{
  "mcpServers": {
    "milano-mobility": {
      "command": "/home/utente/milano-mobility-mcp/.venv/bin/python",
      "args": ["-m", "milano_mobility_mcp"]
    }
  }
}
```

La posizione del file di configurazione dipende dal client. Nessuna variabile segreta richiesta. Non abilitare log degli argomenti nel client se contengono dati personali: il server non registra input e non accetta targhe.

## Esempi dei quattro tool

Argomenti MCP sempre nella forma `{"request": {...}}`. Risposte sotto come estratti; motivazioni e metadati completi vengono restituiti.

### 1. Profilo veicolo esplicito

`check_vehicle_access`:

```json
{
  "request": {
    "vehicle": {
      "category": "M1", "fuel": "elettrico", "euro_class": null,
      "exemptions": "da_verificare", "resident_in_milan": true
    },
    "at": "2026-09-08T12:00:00+02:00",
    "area": "area_b",
    "inside_area_confirmed_by_user": true,
    "destination": "Destinazione dichiarata in Area B, non geocodificata"
  }
}
```

Risultato `decision: "non_determinabile"`, anche per elettrico: restano situazione personale, geografia e misure non coperte. Residenza non significa esenzione. `exemptions: "nessuna_applicabile_dichiarata"` è solo una dichiarazione; usare `da_verificare` se accessi gratuiti, deroghe o MoVe-In potrebbero essere applicabili.

Obbligatori: categoria, alimentazione, classe Euro (`null` esplicito ammesso solo per elettrico), stato deroghe, area e conferma perimetro. Valori enumerati esposti da `list_tools`; categorie/alimentazioni non coperte non vengono assimilate ad altre.

Data/ora ISO 8601 con offset di **Europe/Rome**: `+01:00` in inverno, `+02:00` in estate. Date naive, offset errati, ore locali inesistenti e timestamp numerici rifiutati. Le due occorrenze dell'ora ambigua autunnale si distinguono con l'offset. Nessun divieto prospettico per istanti futuri. Nessuna geocodifica di civici, confini, itinerari o verifica varchi/telecamere.

### 2. Antismog: sconosciuto non è livello zero

`get_active_smog_level`:

```json
{"request": {"territory": "Comune di Milano"}}
```

Risposta: `decision: "non_determinabile"`, `active_level: null`, `authority_status: "non_verificato"`, `authoritative_territory: null`, `valid_from: null`, `valid_until: null`, `last_checked: null`, `freshness: "missing"`.

`evaluated_at` è l'ora della chiamata, **non** la consultazione di un bollettino. Il territorio richiesto non è presentato come ambito di un provvedimento. Le misurazioni ARPA non provano attivazione/revoca; il MVP non converte PM10 in uno stato amministrativo.

### 3. MoVe-In: solo aritmetica dichiarata

`query_movein_allowance`:

```json
{"request": {"km_percorsi": "100.1", "soglia_annuale": "100.4", "distanza_viaggio": "0.2"}}
```

Estratto:

```json
{
  "decision": "non_determinabile", "calculation_status": "calcolato",
  "input_provenance": "user_unverified",
  "km_residui": "0.3", "km_eccedenti": "0",
  "viaggio_nel_budget_dichiarato": true,
  "km_residui_dopo_viaggio": "0.1", "km_eccedenti_dopo_viaggio": "0",
  "authenticated_balance": false
}
```

Numeri dimostrativi, **non soglie normative**. Decimal serializzati come stringhe: preferirle anche negli input. Ammessi 0–1.000.000.000 km, massimo sei decimali (limiti tecnici). Negativi, NaN, infiniti e booleani rifiutati. Sopra soglia il residuo è zero, l'eccedenza esplicita e neppure un viaggio nullo rientra nel budget. Nessun saldo autenticato, rinnovo, soglia spettante o autorizzazione dedotti.

### 4. Costi non coperti

`get_daily_costs`:

```json
{"request": {"area": "area_b", "on_date": "2026-09-08", "tariff": "ordinaria"}}
```

Risposta: `calculation_status: "non_determinabile"`, `ordinary_ticket_eur: null`, `total_due_eur: null`, `activation_deadline_exclusive: null`. Non afferma che Area B sia a pagamento: non è calcolato un costo totale per quell'area.

Anche per Area C il risultato attuale è sconosciuto: [prove mancanti](docs/SOURCES.md). Il motore è predisposto per tariffa ordinaria/scadenza solo con fonte verificata per la data; nessuna tariffa reale è abilitata. Tariffe agevolate/sconosciute non diventano ordinarie. Totale dovuto sempre `null`: non si verifica l'obbligo individuale. Il campo scadenza **esclusiva**, quando sarà supportato, indica attivazione prima di quell'istante, non una scadenza universale di pagamento.

## Fonti, aggiornamento e limiti

[Registro fonti](docs/SOURCES.md): URL, consultazione, regole, periodo e limiti. Catalogo in `src/milano_mobility_mcp/sources.py`, incluso nel package; **nessun aggiornamento automatico** o parametro client per sovrascrivere fonti/orologio.

Consultazione dei riferimenti: **8 settembre 2026**; **nessuna data operativa coperta** da regole/tariffe distribuite. Le pagine comunali necessarie hanno restituito HTTP 403; InfoAria soltanto una shell JavaScript. Le pagine Regione/ARPA leggibili documentano cautele e ruoli, non un bollettino attivo. Il motore impone alle future fonti operative una freschezza massima di 24 ore, **non** una scadenza normativa. Un timestamp nuovo non basta: occorre verifica documentale e temporale. Nessun calendario generale di festivi/sospensioni. Il calcolo MoVe-In è già utilizzabile senza queste fonti mancanti.

Non supportati: storico completo, regole future, tutte le classi/categorie, deroghe e accessi residui, targa, importo personale dovuto, geocodifica, API varchi, funzionamento telecamere, saldo privato MoVe-In, antismog live, pagamento o scraping autenticato. Nessun deploy/acquisto. Repository privato, nessuna licenza aggiunta.

## Test e sviluppo

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -q tests\test_mcp_integration.py
.\.venv\Scripts\python.exe -m pip check
```

Su Unix usare `.venv/bin/python` e separatori `/`. Test offline deterministici: calcoli, input invalidi, timezone/DST, confini, fonti mancanti/scadute/periodi, divieto con unknown, costi sconosciuti non zero. Lo smoke avvia **veri processi** da modulo ed entry point, usa il client SDK per `initialize`, `list_tools`, `call_tool` sui quattro tool, verifica JSON strutturato e sopravvivenza agli input invalidi. CI Windows/Linux, Python 3.11/3.13.

Validazione locale dell'8 settembre 2026: Python 3.13.14, SDK `mcp` 1.30.0; `python -m pytest -q` **122 passati**, inclusi due smoke stdio reali; `python -m pip check` senza problemi. Wheel costruita con `python -m pip wheel . --no-deps --wheel-dir <directory-artifact>` e verificata per package, fonti ed entry point, senza fixture di test. La matrice CI è configurata separatamente: questi risultati locali non attestano da soli gli altri sistemi/interpreti.

Architettura: `models.py` contratti; `catalog.py` provenienza/tempo; `sources.py` snapshot; `service.py` valutazioni con clock interno; `adapters.py` indisponibilità antismog; `server.py` stdio. Nessun log applicativo degli input; stdout solo protocollo MCP.

Prossimi passi: [roadmap](docs/ROADMAP.md).
