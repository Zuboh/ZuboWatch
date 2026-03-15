# ZuboWatch 🎬

Un bot Telegram che consiglia film e serie TV in base al tuo mood, alimentato dall'[API TMDb](https://www.themoviedb.org/). Impara dai tuoi feedback e ricorda cosa hai già visto.

## Funzionalità

- **Raccomandazioni basate sul mood** — scegli uno o più mood e ricevi un consiglio personalizzato
- **Filtro piattaforme** — filtra per le tue subscription (Netflix, Prime Video, Disney+, ecc.)
- **Scoring intelligente** — film classificati per qualità, popolarità e rilevanza del mood
- **Apprendimento personale** — il feedback 👍/👎 aggiusta i pesi dei generi nel tempo
- **Watchlist** — salva film da vedere con 🕐
- **Già visto** — segnala un film con ✅ per non rivederlo mai più proposto
- **Statistiche** — i tuoi generi preferiti, mood più usato e film visti

## Come funziona

1. `/start` — scegli Film o Serie TV
2. Seleziona le tue piattaforme streaming
3. Seleziona uno o più mood
4. Premi **🎲 Consigliami!** — ricevi una raccomandazione con valutazione, trama e dove vederla
5. Usa i bottoni inline per dare feedback o salvare in watchlist

```
[ 👍 ]  [ 👎 ]
[ 🕐 Guarda più tardi ]  [ ✅ Già visto ]
```

Dopo ogni 👍/👎 il bot propone subito il film successivo (editando il messaggio) e aggiorna il tuo profilo.

## Stack

- **Python** 3.11+ con `python-telegram-bot` v20 (async)
- **TMDb API** per metadati film, provider streaming, dettagli
- **PostgreSQL** (Supabase) per persistenza utenti, watchlist e profili
- **asyncpg** per connessioni async al DB con connection pooling
- **Render** per il deploy (Background Worker)

## Setup locale

**1. Clona il repo**

```bash
git clone https://github.com/Zuboh/ZuboWatch.git
cd ZuboWatch
```

**2. Crea un virtual environment e installa le dipendenze**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Crea il database**

Crea un progetto su [Supabase](https://supabase.com), vai su *SQL Editor* e incolla il contenuto di `db/schema.sql`.

**4. Crea un file `.env`**

```
TELEGRAM_TOKEN=il_tuo_token_da_BotFather
TMDB_API_KEY=la_tua_chiave_da_themoviedb.org
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

**5. Avvia il bot**

```bash
python main.py
```

## Deploy su Render

1. Crea un progetto su [Supabase](https://supabase.com) → SQL Editor → esegui `db/schema.sql`
2. Copia la *Connection string (URI)* da *Project Settings → Database*
3. Su [Render](https://render.com) crea un **Background Worker** collegato al repo GitHub
4. Aggiungi le variabili d'ambiente: `TELEGRAM_TOKEN`, `TMDB_API_KEY`, `DATABASE_URL`
5. Il `Procfile` (`worker: python main.py`) viene usato automaticamente

## Comandi

| Comando      | Descrizione                                |
| ------------ | ------------------------------------------ |
| `/start`     | Avvia il bot e scegli il tipo di contenuto |
| `/watchlist` | Mostra la tua lista da guardare            |
| `/stats`     | Le tue statistiche di gusto                |
| `/help`      | Lista dei comandi                          |

> `/clear` è disponibile per azzerare le selezioni correnti.

## Struttura del progetto

```
ZuboWatch/
├── main.py              # Entry point
├── config.py            # Variabili d'ambiente
├── parameters.py        # Dati statici (tipi, mood, piattaforme)
├── Procfile             # Render worker
├── requirements.txt     # Dipendenze
├── .env.example         # Template .env
├── db/
│   └── schema.sql       # Schema PostgreSQL
├── handlers/
│   ├── commands.py      # /start, /clear, /watchlist, /stats, /help
│   └── callbacks.py     # Handler bottoni inline
├── keyboards/
│   └── keyboard.py      # Builder InlineKeyboard
└── utils/
    ├── tmbd.py          # Chiamate API TMDb
    ├── mapper.py        # Mapping mood → ID generi TMDb
    ├── scorer.py        # Algoritmo scoring e selezione pesata
    ├── storage.py       # Persistenza PostgreSQL con asyncpg
    ├── messages.py      # Testi user-facing centralizzati
    └── logger.py        # Logger centralizzato
```

## Note

- Il bot usa `run_polling()`, adatto per sviluppo locale e Render worker (non per webhooks in produzione ad alto traffico)
- Filtri qualità: solo film con `vote_average ≥ 6.5` e `vote_count ≥ 200` vengono considerati (con fallback se il pool è vuoto)
- `DATABASE_URL` con prefisso `postgres://` viene normalizzato automaticamente a `postgresql://`
