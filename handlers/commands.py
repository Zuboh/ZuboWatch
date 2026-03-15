from parameters import PARAMETERS
from keyboards.keyboard import build_keyboard
from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram.ext import ContextTypes
from utils.storage import get_user_selections, clear_user, get_watchlist, get_stats
from utils.messages import HELP_TEXT, STATS_NO_DATA, WATCHLIST_VUOTA
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
        "🧹 Hai azzerato i campi. /start per inziare",
    )
    logger.info(f"Utente {update.effective_user.username} ha usato /clear")

async def watchlist_command_handler(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    watchlist = get_watchlist(user_id)

    if not watchlist:
        await update.message.reply_text(WATCHLIST_VUOTA)
        logger.info(f"Utente {update.effective_user.username} ha richiesto /watchlist (vuota)")
        return

    righe = []
    for film in watchlist:
        generi_str = ", ".join(film.get("generi", []))
        voto = film.get("voto")
        voto_str = f"⭐ Voto: {voto:.1f}" if voto else ""
        meta = "  |  ".join(filter(None, [voto_str, f"🎭 {generi_str}" if generi_str else ""]))
        piattaforma = film.get("piattaforma", "")
        piattaforma_str = f"📺 Dove vederlo: {piattaforma}" if piattaforma else ""
        righe.append(
            f"🎬 *{film['titolo']}* ({film.get('anno', '')})\n"
            f"{meta}\n"
            f"{piattaforma_str}"
        )

    await update.message.reply_text("\n\n".join(righe), parse_mode="Markdown")
    logger.info(f"Utente {update.effective_user.username} ha richiesto /watchlist")


async def help_handler(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")
    logger.info(f"Utente {update.effective_user.username} ha richiesto /help")


async def stats_handler(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = get_stats(user_id)

    nessun_dato = not stats["film_visti"] and not stats["top_generi"] and not stats["mood_preferito"]
    if nessun_dato:
        await update.message.reply_text(STATS_NO_DATA)
        return

    righe = ["📊 *Le tue statistiche*"]
    if stats["top_generi"]:
        righe += ["", "🎭 *Generi preferiti:*"]
        for i, genere in enumerate(stats["top_generi"], 1):
            righe.append(f"{i}. {genere}")
    righe.append("")
    righe.append(f"🎬 Film già visti: {stats['film_visti']}")
    if stats["mood_preferito"]:
        righe.append(f"😊 Mood preferito: {stats['mood_preferito']}")

    await update.message.reply_text("\n".join(righe), parse_mode="Markdown")
    logger.info(f"Utente {update.effective_user.username} ha richiesto /stats")


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