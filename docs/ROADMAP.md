# Roadmap: mobilità e restrizioni

## MVP 0.1

- SDK MCP ufficiale Python, stdio e quattro tool con input/output Pydantic.
- Calcolo MoVe-In esatto sui dati dichiarati, senza autenticazione o autorizzazione implicita.
- Registro dei riferimenti ufficiali e dei limiti della consultazione: nessun divieto/tariffa abilitato nel catalogo attuale.
- Motore verificato con fixture sintetiche: prevalenza del divieto documentato su componenti sconosciute, gate di fonte/tempo e nessun esito positivo da regole mancanti.
- Adapter antismog esplicitamente non disponibile, mai un livello zero inventato.
- Test offline e integrazione con client SDK su entrambi gli entry point; CI Windows/Linux.

## Prima di ampliare la copertura operativa

1. **Aggiornamento fonti:** definire un processo editoriale con confronto dei documenti, verifica degli atti richiamati, responsabile della revisione e test di regressione. Un nuovo timestamp da solo non rinnova una regola. Estendere le date coperte solo dopo verifica di calendario, festività, sospensioni ed efficacia.
2. **Bollettini antismog:** individuare una fonte ufficiale accessibile e condizioni d'uso; documentare formato, territorio, autorità, momento di pubblicazione, decorrenza, revoca e indisponibilità. Implementare un adapter solo dopo questa verifica. Non convertire automaticamente PM10 ARPA in un provvedimento.
3. **Regole veicoli:** completare classi, categorie, alimentazioni, caratteristiche tecniche, deroghe e numero di accessi. Non estendere per analogia benzina a ibridi/GPL o autovetture a merci.
4. **Geografia:** integrare soltanto perimetri ufficiali con versione e precisione note. Distinguere destinazione, percorso, confini e orari; non inferire funzionamento delle telecamere o stato dei varchi.
5. **Costi:** separare tariffa di listino, ammissibilità, importo effettivamente dovuto, attivazione, eventuali altri costi e sanzioni. Aggiungere agevolazioni e modifiche storiche/future soltanto con fonti pertinenti.
6. **Prove necessarie per `consentito`:** copertura completa di tutte le restrizioni applicabili, fonti fresche e territorialmente pertinenti, assenza verificata di divieti temporanei e trattamento corretto delle eccezioni. Fino ad allora nessun via libera.

## Solo con decisione e consenso ulteriori

- Eventuali integrazioni con informazioni personali MoVe-In richiedono un canale realmente disponibile, autorizzato, documentato e una valutazione privacy. Non è presupposta alcuna API del saldo.
- Nessuna interrogazione automatica della targa, pagamento, credenziale, scraping autenticato, deploy o acquisto nel MVP.
- Visibilità del repository e licenza restano decisioni dell'utente; questa roadmap non le modifica.

Urbanistica esclusa dal perimetro.
