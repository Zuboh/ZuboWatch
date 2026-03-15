from utils.mapper import convert_moods_to_genre_ids
from utils.ombd import search_movies
from utils.mapper import convert_type
from parameters import PARAMETERS
from keyboards.keyboard import build_keyboard
from utils.storage import set_user_selection
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.storage import get_user_selections
import random

async def handle_buttons(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    category = context.user_data.get("next_category", "tipo")

    if data == "generate":
        # Recupera tipo e mood
        tipo_set = get_user_selections(user_id, "tipo")
        tipo = next(iter(tipo_set), None) if tipo_set else None
        tipo_api = convert_type(tipo)

        moods = list(get_user_selections(user_id, "mood"))
        genres_ids = convert_moods_to_genre_ids(moods)

        if not tipo_api or not genres_ids:
            await query.answer("⚠ Seleziona prima tipo e mood!", show_alert=True)
            return

        # Ricerca su TMDb
        results = await search_movies(type_=tipo_api, genres=genres_ids)
        if not results:
            await query.answer("Nessun risultato trovato", show_alert=True)
            return

        choice = random.choice(results)
        title = choice.get('title') or choice.get('name', 'N/A')
        year = (choice.get('release_date') or choice.get('first_air_date') or '')[:4]
        await query.message.reply_text(
            f"🎬 {title} ({year})\nhttps://www.themoviedb.org/{tipo_api}/{choice['id']}"
        )
        return

    selected = get_user_selections(user_id, category)
    if data in selected:
        selected.remove(data)
    else:
        selected.add(data)

    set_user_selection(user_id, category, selected)
    await query.answer()

    if category == "tipo":
        context.user_data["next_category"] = "mood"
        next_category = "mood"
        keyboard = build_keyboard(PARAMETERS[next_category], get_user_selections(user_id, next_category))
        await query.edit_message_text(
            text=f"✅ Hai selezionato {', '.join(selected)}!\nOra scegli il mood (puoi selezionare più opzioni):",
            reply_markup=keyboard
        )
    else:
        # categoria mood
        keyboard = build_keyboard(PARAMETERS[category], selected)
        rows = [list(row) for row in keyboard.inline_keyboard]
        if selected:  # almeno un mood selezionato
            rows.append([InlineKeyboardButton("🎲 Genera!", callback_data="generate")])
        keyboard = InlineKeyboardMarkup(rows)

        await query.edit_message_reply_markup(reply_markup=keyboard)