import json
import asyncpg
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from telegram import BotCommand
import config
from utils import storage
from handlers.commands import start, clear, watchlist_command_handler, help_handler, stats_handler
from handlers.callbacks import handle_buttons


async def on_startup(app):
    async def _init_conn(conn):
        await conn.set_type_codec(
            "jsonb",
            encoder=json.dumps,
            decoder=json.loads,
            schema="pg_catalog",
        )
    app.bot_data["db"] = await asyncpg.create_pool(config.DATABASE_URL, init=_init_conn)
    await storage.init_db(app.bot_data["db"])
    await app.bot.set_my_commands([
        BotCommand("start", "Avvia il bot"),
        BotCommand("watchlist", "La tua lista da guardare"),
        BotCommand("stats", "Le tue statistiche"),
        BotCommand("help", "Lista comandi"),
    ])


async def on_shutdown(app):
    if "db" in app.bot_data:
        await app.bot_data["db"].close()


app = (
    ApplicationBuilder()
    .token(config.TOKEN)
    .post_init(on_startup)
    .post_shutdown(on_shutdown)
    .build()
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(CommandHandler("watchlist", watchlist_command_handler))
app.add_handler(CommandHandler("help", help_handler))
app.add_handler(CommandHandler("stats", stats_handler))
app.add_handler(CallbackQueryHandler(handle_buttons))

print("🎬 ZuboWatch è online!")
app.run_polling()
