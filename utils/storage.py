import json
import os

FILE_PATH = "storage.json"

if os.path.exists(FILE_PATH):
    with open(FILE_PATH, "r") as f:
        try:
            user_data = json.load(f)
        except json.JSONDecodeError:
            user_data = {}
else:
    user_data = {}

def save():
    with open(FILE_PATH, "w") as f:
        json.dump(user_data, f, indent=4)

def get_user_selections(user_id: int, category: str) -> set:
    return set(user_data.get(str(user_id), {}).get(category, []))

def set_user_selection(user_id: int, category: str, selections: set):
    uid = str(user_id)
    if uid not in user_data:
        user_data[uid] = {}
    user_data[uid][category] = list(selections)
    save()

def clear_user(user_id: int):
    uid = str(user_id)
    if uid in user_data:
        user_data[uid] = {}
        save()

BOOST_MAX = 1.5
BOOST_MIN = 0.5

def get_profilo_utente(user_id: int) -> dict:
    profilo = user_data.get(str(user_id), {}).get("profilo", {})
    return {"genre_weights": profilo.get("genre_weights", {}), "seen_ids": profilo.get("seen_ids", [])}

def _ensure_profilo(uid: str):
    if uid not in user_data:
        user_data[uid] = {}
    if "profilo" not in user_data[uid]:
        user_data[uid]["profilo"] = {"genre_weights": {}, "seen_ids": []}

def salva_feedback(user_id: int, film_id: int, genre_ids: list[int], like: bool):
    uid = str(user_id)
    _ensure_profilo(uid)
    profilo = user_data[uid]["profilo"]
    delta = 0.1 if like else -0.1
    for genre_id in genre_ids:
        key = str(genre_id)
        current = profilo["genre_weights"].get(key, 1.0)
        profilo["genre_weights"][key] = max(BOOST_MIN, min(BOOST_MAX, current + delta))
    if film_id not in profilo["seen_ids"]:
        profilo["seen_ids"].append(film_id)
    save()


TOP_GENERI_COUNT = 3

def salva_sessione(user_id: int, mood: str, piattaforme: list[str], tipo_api: str, film: dict):
    uid = str(user_id)
    if uid not in user_data:
        user_data[uid] = {}
    anno_raw = (film.get("release_date") or film.get("first_air_date") or "")[:4]
    user_data[uid]["sessione_corrente"] = {
        "mood": mood,
        "piattaforme": piattaforme,
        "tipo_api": tipo_api,
        "ultimo_film_id": film["id"],
        "ultimo_film_genres": film.get("genre_ids", []),
        "ultimo_film_titolo": film.get("title") or film.get("name", "N/A"),
        "ultimo_film_anno": int(anno_raw) if anno_raw.isdigit() else 0,
        "ultimo_film_voto": film.get("vote_average"),
    }
    _ensure_profilo(uid)
    user_data[uid]["profilo"].setdefault("mood_history", []).append(mood)
    save()


def get_sessione(user_id: int) -> dict:
    return user_data.get(str(user_id), {}).get("sessione_corrente", {})


def reset_seen(user_id: int):
    uid = str(user_id)
    _ensure_profilo(uid)
    user_data[uid]["profilo"]["seen_ids"] = []
    save()


def segna_come_visto(user_id: int, film_id: int):
    uid = str(user_id)
    _ensure_profilo(uid)
    seen = user_data[uid]["profilo"]["seen_ids"]
    if film_id not in seen:
        seen.append(film_id)
    save()


def aggiungi_watchlist(user_id: int, film: dict, piattaforma: str):
    uid = str(user_id)
    if uid not in user_data:
        user_data[uid] = {}
    if "watchlist" not in user_data[uid]:
        user_data[uid]["watchlist"] = []
    film_id = film["film_id"]
    if any(f["film_id"] == film_id for f in user_data[uid]["watchlist"]):
        return
    user_data[uid]["watchlist"].append({**film, "piattaforma": piattaforma})
    save()


def get_watchlist(user_id: int) -> list[dict]:
    return user_data.get(str(user_id), {}).get("watchlist", [])


def rimuovi_watchlist(user_id: int, film_id: int):
    uid = str(user_id)
    wl = user_data.get(uid, {}).get("watchlist", [])
    user_data.setdefault(uid, {})["watchlist"] = [f for f in wl if f["film_id"] != film_id]
    save()


def get_stats(user_id: int) -> dict:
    from utils.mapper import GENRE_ID_TO_NAME
    profilo = user_data.get(str(user_id), {}).get("profilo", {})
    genre_weights = profilo.get("genre_weights", {})
    seen_ids = profilo.get("seen_ids", [])
    mood_history = profilo.get("mood_history", [])
    watchlist = user_data.get(str(user_id), {}).get("watchlist", [])

    sorted_genres = sorted(genre_weights.items(), key=lambda x: float(x[1]), reverse=True)
    top_generi = [
        GENRE_ID_TO_NAME[int(gid)]
        for gid, _ in sorted_genres[:TOP_GENERI_COUNT]
        if int(gid) in GENRE_ID_TO_NAME
    ]
    mood_preferito = max(set(mood_history), key=mood_history.count) if mood_history else None
    return {
        "top_generi": top_generi,
        "film_visti": len(seen_ids),
        "mood_preferito": mood_preferito,
        "watchlist_count": len(watchlist),
    }