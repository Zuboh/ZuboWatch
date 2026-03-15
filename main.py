from utils.tmbd import search_movies
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from telegram import BotCommand
from config import TOKEN
from handlers.commands import start, clear, watchlist_command_handler, help_handler, stats_handler
from handlers.callbacks import handle_buttons

async def setup_commands(app):
    await app.bot.set_my_commands([
        BotCommand("start", "Avvia il bot"),
        BotCommand("watchlist", "La tua lista da guardare"),
        BotCommand("stats", "Le tue statistiche"),
        BotCommand("help", "Lista comandi"),
    ])

app = ApplicationBuilder().token(TOKEN).post_init(setup_commands).build()

# comandi
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(CommandHandler("watchlist", watchlist_command_handler))
app.add_handler(CommandHandler("help", help_handler))
app.add_handler(CommandHandler("stats", stats_handler))

# bottoni
app.add_handler(CallbackQueryHandler(handle_buttons))

print("🎬 ZuboWatch è online!")
app.run_polling()