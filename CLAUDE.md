# ZuboWatch

Bot Telegram per raccomandazioni film e serie TV tramite TMDb API.

## Flusso principale

`/start` → scegli tipo (Film/Serie) → scegli piattaforma → scegli mood → genera → risultato con bottoni inline

Dopo ogni 👍/👎 il bot propone automaticamente un nuovo film (edit del messaggio) aggiornando il profilo utente.

## Setup locale

```bash
python -m venv venv && source venv/bin/activate
pip install python-telegram-bot httpx python-dotenv
```

Crea `.env` nella root:
```
TELEGRAM_TOKEN=<token da BotFather>
TMDB_API_KEY=<chiave da themoviedb.org>
```

Avvia:
```bash
python main.py
```

## Comandi utili

- **Run:** `python main.py`
- **Nessun test runner** configurato (nessun file pytest/unittest presente)
- **Comandi bot:** `/start`, `/clear`, `/watchlist`, `/stats`, `/help`

## Architettura

```
ZuboWatch/
├── main.py              # Entry point, setup Application Telegram
├── config.py            # Lettura variabili d'ambiente (.env)
├── parameters.py        # Dati statici: tipi contenuto, mood disponibili
├── storage.json         # Persistenza runtime (auto-generato, non committare con dati reali)
├── handlers/
│   ├── commands.py      # Handler comandi: /start, /clear, /watchlist, /stats, /help
│   └── callbacks.py     # Handler bottoni inline
├── keyboards/
│   └── keyboard.py      # Builder InlineKeyboard
└── utils/
    ├── ombd.py          # Chiamate API TMDb
    ├── mapper.py        # Mapping mood → generi TMDb, normalize_label(), get_mood_question()
    ├── scorer.py        # Algoritmo di scoring e selezione pesata
    ├── storage.py       # Lettura/scrittura storage.json, profilo utente, sessione, watchlist, stats
    ├── messages.py      # Testi user-facing centralizzati (HELP_TEXT, STATS_NO_DATA, WATCHLIST_VUOTA)
    └── logger.py        # Logger centralizzato
```

## Algoritmo di scoring (`utils/scorer.py`)

Ogni film candidato riceve un punteggio:

```
score = (vote_average/10 × 0.4) + (popularity/1000 × 0.3) + (rilevanza_mood × 0.3)
score × boost_genere_personale
```

| Componente | Peso | Fonte |
|---|---|---|
| Qualità (vote_average) | 40% | TMDb vote_average / 10 |
| Popolarità | 30% | TMDb popularity / 1000, clamp 0–1 |
| Rilevanza mood | 30% | generi del film ∩ generi del mood / totale generi mood |
| Boost personale | moltiplicatore | max(genre_weights[g] per g in film) |

Selezione finale: top-10 per score → `random.choices` con pesi proporzionali (non deterministico ma orientato verso i migliori).

Film già visti (`seen_ids`) vengono esclusi. Se tutti i candidati sono già visti, si riusa il pool completo.

Filtri qualità: applicati lato client dopo la risposta TMDb (`vote_average ≥ 6.5`, `vote_count ≥ 200`), con fallback a tutti i risultati se il pool sarebbe vuoto.

## Mappa mood → generi TMDb (`utils/mapper.py`)

| Mood | Generi TMDb | ID |
|---|---|---|
| Azione | Action, Adventure, Thriller | 28, 12, 53 |
| Comico | Comedy | 35 |
| Drammatico | Drama, Romance | 18, 10749 |
| Riflessivo | Drama, Mystery, Sci-Fi | 18, 9648, 878 |
| Horror | Horror, Thriller | 27, 53 |
| Romance | Romance, Drama | 10749, 18 |

Con più mood selezionati i generi vengono uniti (OR): TMDb riceve `28|12|53|35`.

`get_mood_question()` restituisce una domanda contestuale all'orario (mattina/pomeriggio/sera/notte).

**Per aggiungere un mood:** aggiungi la voce in `parameters.py:PARAMETERS["mood"]` e la mappatura in `mapper.py:MOOD_TO_GENRES` con la stessa chiave normalizzata (prima parola, capitalize).

## Schema completo `storage.json`

```json
{
  "user_id": {
    "tipo": ["Film"],
    "piattaforma": ["Netflix"],
    "mood": ["Azione"],
    "profilo": {
      "genre_weights": { "28": 1.2, "35": 0.8 },
      "seen_ids": [123, 456],
      "mood_history": ["Azione", "Horror", "Azione"]
    },
    "sessione_corrente": {
      "mood": "Azione",
      "piattaforme": ["Netflix"],
      "tipo_api": "movie",
      "ultimo_film_id": 456,
      "ultimo_film_genres": [28, 53],
      "ultimo_film_titolo": "Mad Max",
      "ultimo_film_anno": 2015,
      "ultimo_film_voto": 7.6
    },
    "watchlist": [
      {
        "film_id": 123,
        "titolo": "Inception",
        "anno": 2010,
        "generi": ["Azione", "Fantascienza"],
        "voto": 8.4,
        "piattaforma": "Netflix"
      }
    ]
  }
}
```

- `genre_weights`: boost/malus per genere, inizia a 1.0, range [0.5, 1.5], delta ±0.1 per feedback
- `seen_ids`: film già proposti, esclusi dalla selezione finché non esauriti
- `mood_history`: lista dei mood usati nelle sessioni, usata da `get_stats()` per calcolare il mood preferito
- `sessione_corrente`: contesto dell'ultima raccomandazione, usato per il ciclo feedback → prossimo film
- `watchlist`: film salvati con 🕐; i metadati vengono sempre da TMDb al momento del salvataggio

## Bottoni inline dopo ogni film

```
[ 👍 ]  [ 👎 ]
[ 🕐 Guarda più tardi ]  [ ✅ Già visto ]
```

**Flusso 👍/👎 (`like_{id}` / `dislike_{id}`):**
1. Aggiorna `genre_weights` nel profilo (±0.1, clamp [0.5, 1.5])
2. Aggiunge il film a `seen_ids`
3. Recupera nuovi candidati dalla sessione corrente
4. Seleziona il prossimo film con `scorer.pick_best`
5. Edita il messaggio con il nuovo film

**Flusso 🕐 Guarda più tardi (`watchlist_{film_id}`):**
1. Chiama `get_details` e `get_watch_providers` su TMDb con `film_id` da `callback_data` — i metadati vengono sempre dall'API, mai dalla sessione (la sessione potrebbe già essere aggiornata a un film successivo)
2. Chiama `aggiungi_watchlist()` (idempotente: ignora duplicati)
3. Rimuove i bottoni 🕐 e ✅, mantiene 👍 👎
4. Risposta inline: "🕐 Salvato in watchlist!"

**Flusso ✅ Già visto (`gia_visto_{film_id}`):**
1. Chiama `segna_come_visto()` → aggiunge a `seen_ids`
2. Edita il messaggio: "L'hai già visto! Ti è piaciuto?"
3. Mostra bottoni 👍/👎 → stesso flusso feedback normale

## Comandi

**`/watchlist`**: mostra la lista salvata formattata (titolo, voto, generi, piattaforma). `parse_mode="Markdown"`.

**`/stats`**: chiama `storage.get_stats(user_id)`. Calcola:
- `top_generi`: top-3 generi per `genre_weight` più alto, convertiti in nomi via `GENRE_ID_TO_NAME`
- `film_visti`: `len(seen_ids)`
- `mood_preferito`: mood più frequente in `mood_history`
- `watchlist_count`: `len(watchlist)`

Se nessun dato ancora disponibile, mostra `STATS_NO_DATA` da `utils/messages.py`.

**`/help`**: testo statico `HELP_TEXT` da `utils/messages.py`.

**`/clear`**: resetta tipo/piattaforma/mood (non tocca profilo, watchlist o storico).

## Come estendere

**Aggiungere un mood:**
1. `parameters.py` → aggiungi stringa in `PARAMETERS["mood"]`
2. `mapper.py:MOOD_TO_GENRES` → aggiungi `"NuovoMood": [id1, id2, ...]`

**Cambiare i pesi dell'algoritmo:**
Costanti in `scorer.py` (i tre pesi devono sommare a 1.0).

**Cambiare il range boost/malus:**
`storage.py:BOOST_MAX` e `BOOST_MIN`. Delta fisso a `0.1` in `salva_feedback`.

**Aggiungere un testo del bot:**
Aggiungi la costante in `utils/messages.py` e importala nell'handler.

## Convenzioni codice

- Tutto **async/await** (python-telegram-bot v20+)
- **Type hints** su ogni funzione
- `normalize_label()` in `mapper.py` gestisce strip emoji + capitalize per le label
- Storage: set in memoria → list in JSON (conversione gestita in `storage.py`)
- Usa `utils/logger.py` per il logging, **non `print()`** (eccezione: errori TMDb)
- Nessuna logica di scoring fuori da `scorer.py`
- Nessuna chiamata TMDb fuori da `ombd.py`
- Nessun `if mood == ...` fuori da `mapper.py`
- Testi user-facing in `utils/messages.py`, mai hardcodati negli handler

## Avvertenze

- `storage.json` è auto-generato a runtime — non committarlo con dati utenti reali
- `context.user_data` (Telegram) traccia solo `next_category`; lo stato principale vive in `storage.json`
- TMDb API key **solo in `.env`**, mai hardcoded nel codice
- Il bot usa `run_polling()` (non webhooks) — adatto per sviluppo/uso locale, non per produzione
- Il menu comandi Telegram si aggiorna solo al riavvio del bot (via `post_init`)
