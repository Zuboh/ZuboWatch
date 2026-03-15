# ZuboWatch 🎬

A Telegram bot that recommends movies and TV series based on your mood, powered by the [TMDb API](https://www.themoviedb.org/). It learns from your feedback and remembers what you've already seen.

## Features

- **Mood-based recommendations** — choose one or more moods and get a scored suggestion
- **Platform filter** — filter by your streaming subscriptions (Netflix, Prime Video, Disney+, etc.)
- **Smart scoring** — recommendations ranked by quality, popularity, and mood relevance
- **Personal learning** — 👍/👎 feedback adjusts your genre preferences over time
- **Watchlist** — save films to watch later with 🕐
- **Already seen** — mark films as seen with ✅ so they're never proposed again
- **Stats** — see your top genres, mood trends, and films watched

## How it works

1. `/start` — choose Movie or TV Series
2. Select your streaming platforms
3. Select one or more moods
4. Tap **🎲 Consigliami!** — get a recommendation with rating, overview, and where to watch
5. Use the inline buttons to give feedback or save to your watchlist

```
[ 👍 ]  [ 👎 ]
[ 🕐 Guarda più tardi ]  [ ✅ Già visto ]
```

After each 👍/👎, the bot immediately proposes the next film (edits the message) and updates your profile.

## Setup

**1. Clone the repo**

```bash
git clone https://github.com/Zuboh/ZuboWatch.git
cd ZuboWatch
```

**2. Create a virtual environment and install dependencies**

```bash
python -m venv venv
source venv/bin/activate
pip install python-telegram-bot httpx python-dotenv
```

**3. Create a `.env` file**

```
TELEGRAM_TOKEN=your_token_from_BotFather
TMDB_API_KEY=your_key_from_themoviedb.org
```

**4. Run the bot**

```bash
python main.py
```

## Commands

| Command      | Description                           |
| ------------ | ------------------------------------- |
| `/start`     | Start the bot and pick a content type |
| `/watchlist` | Show your saved films                 |
| `/stats`     | Your taste in numbers                 |
| `/help`      | List all commands                     |

> `/clear` is also available to reset all selections.

## Project structure

```
ZuboWatch/
├── main.py              # Entry point
├── config.py            # Environment variables
├── parameters.py        # Static data (types, moods, platforms)
├── handlers/
│   ├── commands.py      # /start, /clear, /watchlist, /stats, /help
│   └── callbacks.py     # Inline button handlers
├── keyboards/
│   └── keyboard.py      # InlineKeyboard builder
└── utils/
    ├── tmdb.py          # TMDb API calls
    ├── mapper.py        # Mood → genre ID mapping, time-based mood question
    ├── scorer.py        # Scoring algorithm and weighted random pick
    ├── storage.py       # JSON persistence, user profile, watchlist, stats
    ├── messages.py      # All user-facing text strings
    └── logger.py        # Centralized logger
```

## Notes

- `storage.json` is auto-generated at runtime — do not commit it with real user data
- The bot uses `run_polling()`, suitable for local development only (not production webhooks)
- Quality filters: only films with `vote_average ≥ 6.5` and `vote_count ≥ 200` are considered (with fallback if the pool is empty)
