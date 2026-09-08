# Milano Mobility MCP

Server MCP Python per aiutare cittadini e pendolari a interpretare le restrizioni alla circolazione a Milano, con calcoli deterministici e fonti ufficiali verificabili.

## Stato

Repository inizializzato; MVP in preparazione. Non usare il progetto come autorizzazione alla circolazione o garanzia contro sanzioni.

## Perimetro

- Area B e Area C del Comune di Milano.
- MoVe-In della Regione Lombardia: stime esplicite basate sui dati forniti dall'utente; nessun accesso presunto al saldo personale.
- Misure temporanee antismog: distinguere misurazioni ARPA e provvedimenti dell'autorita competente.
- Costi e scadenze: soltanto quando supportati da regole ufficiali valide per la data richiesta.

## Tool previsti

- `check_vehicle_access`: valutazione motivata, con esiti consentito, vietato o non determinabile.
- `get_active_smog_level`: stato ufficiale, territorio, validita e freschezza; stato sconosciuto se non verificabile.
- `query_movein_allowance`: budget chilometrico residuo e simulazione di un tragitto, non prova di autorizzazione.
- `get_daily_costs`: ticket e scadenze documentati, oppure risultato non determinabile.

## Principi

Nessuna API, tariffa, deroga o classe ambientale inventata. Dati mancanti, scaduti o futuri non verificabili non devono produrre un via libera. Ogni regola operativa deve riportare fonte e periodo di validita. Nessun pagamento automatico, credenziale o dato personale nel repository.

## Roadmap iniziale

1. Verificare fonti ufficiali e accessibilita tecnica dei dati.
2. Implementare server MCP via stdio e modelli strutturati.
3. Aggiungere calcoli deterministici, gestione degli esiti non determinabili e test offline.
4. Documentare installazione, configurazione dei client e limiti delle integrazioni.