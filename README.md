# ZuboWatch 🎬

A Telegram bot that recommends random movies and TV series based on your mood, powered by the [TMDb API](https://www.themoviedb.org/).

## How it works

1. `/start` — choose a content type (Movie or TV Series)
2. Select one or more moods (Action, Comedy, Horror, etc.)
3. Tap **Generate** — get a random recommendation with a TMDb link

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

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and pick a content type |
| `/clear` | Reset all selections |
| `/show` | Show current selections |

## Project structure

```
ZuboWatch/
├── main.py              # Entry point
├── config.py            # Environment variables
├── parameters.py        # Static data (types, moods)
├── handlers/            # Telegram command and callback handlers
├── keyboards/           # InlineKeyboard builders
└── utils/
    ├── tmdb.py          # TMDb API calls
    ├── mapper.py        # Mood → genre ID mapping
    ├── storage.py       # JSON persistence
    └── logger.py        # Centralized logger
```

## Notes

- `storage.json` is auto-generated at runtime — do not commit it with real user data
- The bot uses `run_polling()`, suitable for local development only (not production webhooks)
