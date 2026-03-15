import random

TOP_N = 10
MIN_SCORE_WEIGHT = 0.1
BOOST_MAX = 1.5
BOOST_MIN = 0.5

def calcola_score(film: dict, mood: str, profilo: dict) -> float:
    from utils.mapper import mood_to_genres
    vote = film.get("vote_average", 0) / 10
    popularity = min(film.get("popularity", 0) / 1000, 1.0)
    film_genres = film.get("genre_ids", [])
    mood_genres = mood_to_genres(mood)
    rilevanza = sum(1 for g in film_genres if g in mood_genres) / len(mood_genres) if mood_genres else 0.0
    base = (vote * 0.4) + (popularity * 0.3) + (rilevanza * 0.3)
    genre_weights = profilo.get("genre_weights", {})
    boost = max((genre_weights.get(str(g), 1.0) for g in film_genres), default=1.0)
    return base * boost

def weighted_random_pick(films_scorati: list[dict]) -> dict:
    top = sorted(films_scorati, key=lambda f: f["_score"], reverse=True)[:TOP_N]
    scores = [max(f["_score"], MIN_SCORE_WEIGHT) for f in top]
    total = sum(scores)
    weights = [s / total for s in scores]
    return random.choices(top, weights=weights, k=1)[0]

def pick_best(candidates: list[dict], profilo: dict, mood: str) -> dict:
    seen_ids = set(profilo.get("seen_ids", []))
    pool = [f for f in candidates if f["id"] not in seen_ids]
    if not pool:
        pool = candidates  # tutti visti: riusa il pool completo senza seen_ids
    scored = [{**f, "_score": calcola_score(f, mood, profilo)} for f in pool]
    return weighted_random_pick(scored)
