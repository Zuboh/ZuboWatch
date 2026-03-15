from parameters import PARAMETERS
from keyboards.keyboard import build_keyboard
from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram.ext import ContextTypes
from utils.storage import get_user_selections, clear_user
from utils.logger import logger

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    clear_user(user_id)

    context.user_data["next_category"] = "tipo"
    selected = get_user_selections(user_id, "tipo")

    keyboard = build_keyboard(PARAMETERS["tipo"], selected)

    await update.message.reply_text(
        "🎬 Benvenuto su ZuboWatch!\nSeleziona il tipo di contenuto:",
        reply_markup=keyboard
    )
    logger.info(f"Utente {update.effective_user.username} ha aperto /start")

async def clear(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    clear_user(user_id)

    await update.message.reply_text(
        "🧹 Hai azzerato i campi.\n      /start per inziare",
    )
    logger.info(f"Utente {update.effective_user.username} ha usato /clear")

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tipo = get_user_selections(user_id, "tipo")
    mood = get_user_selections(user_id, "mood")

    parts = []
    if tipo:
        parts.append(f"Tipo: {', '.join(tipo)}")
    if mood:
        parts.append(f"Mood: {', '.join(mood)}")
    msg = "Selezioni attive:\n" + "\n".join(parts) if parts else "Non hai ancora selezionato nulla."

    await update.message.reply_text(msg)
    logger.info(f"Utente {update.effective_user.username} ha richiesto /show")