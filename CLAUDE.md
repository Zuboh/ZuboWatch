# ZuboWatch

Bot Telegram per raccomandazioni film e serie TV tramite TMDb API.

## Flusso principale
`/start` → scegli tipo (Film/Serie) → scegli mood → genera → risultato casuale

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
- **Comandi bot:** `/start`, `/clear`, `/show`

## Architettura

```
ZuboWatch/
├── main.py              # Entry point, setup Application Telegram
├── config.py            # Lettura variabili d'ambiente (.env)
├── parameters.py        # Dati statici: tipi contenuto, mood disponibili
├── storage.json         # Persistenza runtime (auto-generato, non committare con dati reali)
├── handlers/            # Handler comandi e callback Telegram
├── keyboards/           # Builder InlineKeyboard
└── utils/
    ├── tmdb.py          # Chiamate API TMDb
    ├── mapper.py        # Mapping mood → generi TMDb, normalize_label()
    ├── storage.py       # Lettura/scrittura storage.json
    └── logger.py        # Logger centralizzato
```

## Convenzioni codice

- Tutto **async/await** (python-telegram-bot v20+)
- **Type hints** con union syntax moderna (`str | None`)
- `normalize_label()` in `mapper.py` gestisce strip emoji + capitalize per le label
- Storage: set in memoria → list in JSON (conversione gestita in `storage.py`)
- Usa `utils/logger.py` per il logging, **non `print()`** (eccezione: errori TMDb)

## Avvertenze

- `storage.json` è auto-generato a runtime — non committarlo con dati utenti reali
- `context.user_data` (Telegram) traccia solo `next_category`; lo stato principale vive in `storage.json`
- **Da allineare:** `mapper.py:MOOD_TO_GENRES` usa `"Romantico"` ma `parameters.py` usa `"Romance"`
- TMDb API key **solo in `.env`**, mai hardcoded nel codice
- Il bot usa `run_polling()` (non webhooks) — adatto per sviluppo/uso locale, non per produzione
