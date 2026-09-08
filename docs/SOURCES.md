# Registro delle fonti e confine delle prove

Consultazione: **8 settembre 2026**, fuso Europe/Rome. Ricerca limitata a risorse pubbliche ufficiali Comune di Milano, Regione Lombardia e ARPA Lombardia. Nessun accesso autenticato, nessuna interrogazione targa o saldo personale.

## Esito operativo, senza ambiguità

**Nessun divieto Area B/C, tariffa o scadenza Area C è abilitato nel catalogo distribuito. Nessun livello antismog live è stato acquisito.** L'MVP funziona via MCP, calcola il budget MoVe-In e restituisce risultati strutturati di indisponibilità negli altri casi, con questi riferimenti e limiti. Non contiene un numero di tariffa, una soglia normativa o una classe vietata dedotti da esempi o risultati di ricerca.

I test esercitano il motore anche con divieti e tariffe **sintetici**, esclusivamente in `tests/`. Non sono dati normativi e non sono importati dal server. Il catalogo operativo `PUBLIC_SNAPSHOT` contiene zero regole e zero tariffe. Nessuna data di servizio è considerata verificata solo perché coincide con la consultazione.

## Comune di Milano: prove operative non acquisite

| ID / risorsa ufficiale | Riscontro della consultazione | Validità e limite |
|---|---|---|
| `comune-area-b` — [Area B](https://www.comune.milano.it/argomenti/mobilita/area-b) | HTTP 403, anche con normale richiesta HTTP alternativa | Nessun testo direttamente verificato: orari, divieti, deroghe e decorrenza non abilitati. |
| `comune-area-b-calendario` — [Calendario dei divieti](https://www.comune.milano.it/argomenti/mobilita/area-b-calendario-dei-divieti) | HTTP 403 | Nessun calendario o giorno di applicazione verificato. |
| `comune-area-b-euro0` — [Posso accedere ad Area B con un veicolo a benzina Euro 0?](https://servizicrm.comune.milano.it/centro-supporto/KA-01272/Accesso-Area-B-per-veicoli-benzina-Euro-) | HTTP 403 | Titolo individuato nella ricerca, non prova sufficiente di divieto vigente. |
| `comune-area-c-ticket` — [Come si acquistano i ticket Area C?](https://servizicrm.comune.milano.it/centro-supporto/KA-01154/Acquisto-ticket-Area-C) | HTTP 403 | Nessuna tariffa o scadenza di attivazione verificata per la data richiesta. |
| `comune-area-c-pdf` — [Area C nuove tariffe dal 2023 Area C.pdf](https://www.comune.milano.it/documents/20118/35188/Area+C+nuove+tariffe+dal+2023+Area+C.pdf/5ee21a73-7301-60c7-d2fe-5e2f77e8a158?version=1.0&t=1746021538283&download=true) | HTTP 200, PDF di 44.900 byte; contenuto non verificato nella ricerca | Disponibilità e nome del file non attestano la vigenza al 2026-09-08. Nessuna tariffa estratta o abilitata. |

Per tutte queste risorse: data di pubblicazione, decorrenza normativa, termine di validità e copertura di date operative **non verificati**. I riassunti dei motori di ricerca non sono stati promossi a prove normative. Il 403 indica un limite della consultazione, non che la pagina non esista o sia irraggiungibile per ogni browser.

## Regione Lombardia e ARPA: contesto verificato, non stato live

### `regione-misure-temporanee`

- Fonte: [Misure temporanee per migliorare la qualità dell'aria](https://www.regione.lombardia.it/ambiente-e-territorio/qualita-dell-aria/red-misure-temporanee-per-miglioramento-qualita-aria), Regione Lombardia.
- Riscontro: HTTP 200, testo leggibile. Aggiornamento dichiarato: **16 luglio 2026**.
- Riscontro testuale breve: «È attivo il sito INFOARIA». La pagina descrive informazioni sulle misure temporanee e notifiche di attivazione, rinviando al sito regionale.
- Cita la d.G.r. n. 5613 del 12 gennaio 2026 e una finestra stagionale; l'allegato non è stato verificato separatamente. **Non vengono tradotti in regole o livelli attivi.**
- Validità: pagina informativa, non bollettino con territorio e periodo di attivazione. Decorrenza e scadenza di un provvedimento concreto non acquisite.

### `regione-infoaria`

- Fonte: [Info Aria](https://www.infoaria.regione.lombardia.it/infoaria/#/home), collegamento indicato dalla Regione.
- Riscontro: HTTP 200; soltanto una shell HTML/JavaScript di 686 byte, senza bollettino leggibile nella consultazione.
- Nessun livello ufficiale, timestamp del bollettino, territorio o periodo acquisito.
- Un HTTP 200 **non** equivale a stato verificato. L'adapter runtime non effettua chiamate e restituisce `active_level`, `last_checked`, `valid_from`, `valid_until` a `null`.
- `checked_on` del riferimento documenta questa consultazione; non popola `last_checked` di uno stato antismog mai verificato.

### `arpa-aria`

- Fonte: [ARPA Lombardia — Aria](https://www.arpalombardia.it/temi-ambientali/aria/).
- Riscontro: HTTP 200, testo leggibile. Ultimo aggiornamento dichiarato: **9 settembre 2025**.
- Riscontro breve: «misurati dalla rete di rilevamento». Il testo descrive anche stime mediante modelli matematici.
- Si tratta del ruolo e dei prodotti di misura/stima della qualità dell'aria, **non** della prova che un provvedimento sia attivo o revocato.
- Nessuna attribuzione di poteri di attivazione ad ARPA dedotta da queste misurazioni. Ogni eventuale misura avrebbe timestamp e validazione propri, non acquisiti qui.

### `regione-movein`

- Fonte: [Servizio MoVe-In](https://www.regione.lombardia.it/ambiente-e-territorio/qualita-dell-aria/servizio-move-in), Regione Lombardia.
- Riscontro: HTTP 200, testo leggibile. Aggiornamento dichiarato: **21 maggio 2026**.
- Il testo verificato precisa che la limitazione chilometrica MoVe-In non si applica quando vengono attivate misure temporanee; descrive inoltre il limite rispetto alle ZTL comunali, salvo estensione approvata dal Comune.
- Area B è menzionata come esempio di estensione. **Area C non è esplicitamente nominata nel testo recuperato**: non si presenta questa pagina come una citazione specifica su Area C.
- Conseguenza prudente: disponibilità di chilometri o adesione non provano autorizzazione Area C e non superano misure antismog. Queste cautele non sono usate per produrre un nuovo divieto individuale.
- Nessuna soglia spettante, percorrenza personale, saldo autenticato o decorrenza individuale acquisita. Il tool sottrae e confronta esclusivamente i tre valori utente.

Le date dichiarate dalle pagine sono metadati editoriali, **non date di entrata in vigore o scadenza delle norme**. Per tutti i riferimenti `legal_valid_from`/`legal_valid_through` restano `null`; `rule_validity` è `non_verificata` e `freshness` è `reference_only`. Questo non nega la leggibilità delle pagine regionali: impedisce di scambiarle per prove operative complete.

## Aggiornamento e criteri di abilitazione

Il package non scarica né aggiorna automaticamente fonti. I riferimenti riportano una consultazione storica, non una verifica ad ogni chiamata. Per abilitare una regola o tariffa occorrono:

1. testo ufficiale direttamente verificato, con condizioni pertinenti e rimandi normativi controllati;
2. territorio, profilo, giorni/orari, eccezioni e periodo di efficacia documentati;
3. distinzione tra periodo normativo, periodo coperto dal motore e ultima consultazione;
4. date di servizio verificate anche rispetto a festività/sospensioni, senza inferenze dal solo giorno della settimana;
5. un record `Source` e relativi test; nessuna fixture sintetica nel catalogo distribuito.

Il motore richiede `official_public`, consulta `coverage_from`/`coverage_through`, rispetta eventuali date normative e applica una freschezza tecnica massima di **24 ore** dalla consultazione (o inferiore se `fresh_until` è anteriore). Con fonte futura, scaduta, assente, non verificata o fuori copertura, l'esito resta sconosciuto. La scadenza tecnica non è la fine della norma. La produzione attuale non ha fonti operative da rinnovare: è necessario acquisire prima le prove mancanti, non cambiare soltanto un timestamp.

Nessuna dichiarazione di circolazione consentita fino alla copertura completa. Nessuna inferenza sul funzionamento di telecamere, disponibilità di varchi o autorizzazioni personali. Per la continuazione: [roadmap](ROADMAP.md).
