from utils.mapper import convert_type, convert_platforms_to_provider_ids, get_mood_question
from utils.tmbd import fetch_candidates, get_details, get_watch_providers
from utils.storage import (
    set_user_selection,
    get_user_selections,
    salva_feedback,
    get_profilo_utente,
    salva_sessione,
    get_sessione,
    aggiungi_watchlist,
    segna_come_visto,
)
from utils import scorer
from parameters import PARAMETERS
from keyboards.keyboard import build_keyboard
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio


async def _formatta_film(tipo_api: str, film: dict) -> tuple[str, InlineKeyboardMarkup]:
    film_id = film["id"]
    details, providers_list = await asyncio.gather(
        get_details(tipo_api, film_id),
        get_watch_providers(tipo_api, film_id),
    )
    title = film.get("title") or film.get("name", "N/A")
    year = (film.get("release_date") or film.get("first_air_date") or "")[:4]
    vote = details.get("vote_average")
    runtime = details.get("runtime") or (details.get("episode_run_time") or [None])[0]
    overview = details.get("overview") or "Trama non disponibile."

    vote_str = f"⭐ {vote:.1f}/10" if vote else ""
    runtime_str = f"⏱ {runtime} min" if runtime else ""
    meta = "  ".join(filter(None, [vote_str, runtime_str]))

    provider_str = ""
    if providers_list:
        provider_str = "\n\n📺 Dove vederlo (IT):\n" + "\n".join(f"• {p}" for p in providers_list)

    text = (
        f"🎬 {title} ({year})\n"
        f"{meta}\n\n"
        f"📖 {overview}"
        f"{provider_str}\n\n"
        f"🔗 https://www.themoviedb.org/{tipo_api}/{film_id}"
    )
    feedback_kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👍", callback_data=f"like_{film_id}"),
            InlineKeyboardButton("👎", callback_data=f"dislike_{film_id}"),
        ],
        [
            InlineKeyboardButton("🕐 Guarda più tardi", callback_data=f"watchlist_{film_id}"),
            InlineKeyboardButton("✅ Già visto", callback_data=f"gia_visto_{film_id}"),
        ],
    ])
    return text, feedback_kb


async def _gestisci_feedback(query, user_id: int, data: str) -> None:
    like = data.startswith("like_")
    film_id = int(data.split("_", 1)[1])

    sessione = get_sessione(user_id)
    genre_ids = sessione.get("ultimo_film_genres", [])
    salva_feedback(user_id, film_id, genre_ids, like)

    tipo_api = sessione.get("tipo_api", "movie")
    mood = sessione.get("mood", "")
    piattaforme = sessione.get("piattaforme", [])
    provider_ids = convert_platforms_to_provider_ids(piattaforme)

    candidates = await fetch_candidates(tipo_api, [mood], provider_ids)
    profilo = get_profilo_utente(user_id)
    nuovo_film = scorer.pick_best(candidates, profilo, mood)

    salva_sessione(user_id, mood, piattaforme, tipo_api, nuovo_film)
    text, feedback_kb = await _formatta_film(tipo_api, nuovo_film)
    await query.edit_message_text(text, reply_markup=feedback_kb)
    await query.answer("✅ Grazie!" if like else "👎 Capito!")


async def _genera_film(query, user_id: int) -> None:
    tipo_set = get_user_selections(user_id, "tipo")
    tipo = next(iter(tipo_set), None)
    tipo_api = convert_type(tipo)

    moods = list(get_user_selections(user_id, "mood"))
    piattaforme = list(get_user_selections(user_id, "piattaforma"))
    provider_ids = convert_platforms_to_provider_ids(piattaforme)

    if not tipo_api or not moods:
        await query.answer("⚠ Seleziona tipo, piattaforma e mood!", show_alert=True)
        return

    candidates = await fetch_candidates(tipo_api, moods, provider_ids)
    if not candidates:
        await query.answer("Nessun risultato trovato", show_alert=True)
        return

    profilo = get_profilo_utente(user_id)
    mood_principale = moods[0]
    choice = scorer.pick_best(candidates, profilo, mood_principale)

    salva_sessione(user_id, mood_principale, piattaforme, tipo_api, choice)
    text, feedback_kb = await _formatta_film(tipo_api, choice)
    await query.answer()
    await query.message.reply_text(text, reply_markup=feedback_kb)


async def _gestisci_watchlist(query, user_id: int, film_id: int) -> None:
    sessione = get_sessione(user_id)
    tipo_api = sessione.get("tipo_api", "movie")

    details, providers_list = await asyncio.gather(
        get_details(tipo_api, film_id),
        get_watch_providers(tipo_api, film_id),
    )
    anno_raw = (details.get("release_date") or details.get("first_air_date") or "")[:4]
    film = {
        "film_id": film_id,
        "titolo": details.get("title") or details.get("name", "N/A"),
        "anno": int(anno_raw) if anno_raw.isdigit() else 0,
        "generi": [g["name"] for g in details.get("genres", [])],
        "voto": details.get("vote_average"),
    }
    piattaforma = providers_list[0] if providers_list else (sessione.get("piattaforme") or [""])[0]
    aggiungi_watchlist(user_id, film, piattaforma)

    solo_feedback_kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("👍", callback_data=f"like_{film_id}"),
        InlineKeyboardButton("👎", callback_data=f"dislike_{film_id}"),
    ]])
    await query.edit_message_reply_markup(reply_markup=solo_feedback_kb)
    await query.answer("🕐 Salvato in watchlist!")


async def _gestisci_gia_visto(query, user_id: int, film_id: int) -> None:
    segna_come_visto(user_id, film_id)

    risposta_kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("👍 Sì, era bello", callback_data=f"like_{film_id}"),
        InlineKeyboardButton("👎 No, non mi è piaciuto", callback_data=f"dislike_{film_id}"),
    ]])
    await query.edit_message_text("L'hai già visto! Ti è piaciuto?", reply_markup=risposta_kb)
    await query.answer()


async def handle_buttons(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    category = context.user_data.get("next_category", "tipo")

    if data.startswith("like_") or data.startswith("dislike_"):
        await _gestisci_feedback(query, user_id, data)
        return

    if data.startswith("watchlist_"):
        await _gestisci_watchlist(query, user_id, int(data.split("_", 1)[1]))
        return

    if data.startswith("gia_visto_"):
        await _gestisci_gia_visto(query, user_id, int(data.split("_", 1)[1]))
        return

    if data == "next_mood":
        context.user_data["next_category"] = "mood"
        platforms = get_user_selections(user_id, "piattaforma")
        keyboard = build_keyboard(PARAMETERS["mood"], get_user_selections(user_id, "mood"))
        await query.edit_message_text(
            text=f"✅ Piattaforme: {', '.join(platforms)}!\n{get_mood_question()}",
            reply_markup=keyboard,
        )
        return

    if data == "generate":
        await _genera_film(query, user_id)
        return

    selected = get_user_selections(user_id, category)
    if data in selected:
        selected.remove(data)
    else:
        selected.add(data)

    set_user_selection(user_id, category, selected)
    await query.answer()

    if category == "tipo":
        context.user_data["next_category"] = "piattaforma"
        next_cat = "piattaforma"
        keyboard = build_keyboard(PARAMETERS[next_cat], get_user_selections(user_id, next_cat))
        await query.edit_message_text(
            text=f"✅ Hai selezionato {', '.join(selected)}!\nOra scegli le piattaforme che possiedi: ",
            reply_markup=keyboard,
        )
    elif category == "piattaforma":
        keyboard = build_keyboard(PARAMETERS[category], selected)
        rows = [list(row) for row in keyboard.inline_keyboard]
        if selected:
            rows.append([InlineKeyboardButton("Avanti →", callback_data="next_mood")])
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(rows))
    else:  # mood
        keyboard = build_keyboard(PARAMETERS[category], selected)
        rows = [list(row) for row in keyboard.inline_keyboard]
        if selected:
            rows.append([InlineKeyboardButton("🎲 Consigliami!", callback_data="generate")])
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(rows))
