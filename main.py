from utils.ombd import search_movies
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from telegram import BotCommand
from config import TOKEN
from handlers.commands import start, clear, show
from handlers.callbacks import handle_buttons

async def setup_commands(app):
    await app.bot.set_my_commands([
        BotCommand("start", "Avvia il bot e seleziona il tipo di contenuto"),
        BotCommand("clear", "Pulisce tutte le selezioni e ricomincia"),
        BotCommand("show", "Mostra le selezioni attive")
    ])

app = ApplicationBuilder().token(TOKEN).post_init(setup_commands).build()

# comandi
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(CommandHandler("show", show))

# bottoni
app.add_handler(CallbackQueryHandler(handle_buttons))

print("🎬 ZuboWatch è online!")
app.run_polling()