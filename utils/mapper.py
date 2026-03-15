MOOD_TO_GENRES = {
    "Azione": [28, 12, 53],        # Action, Adventure, Thriller
    "Comico": [35],                # Comedy
    "Drammatico": [18, 10749],     # Drama, Romance
    "Riflessivo": [18, 9648, 878], # Drama, Mystery, Sci-Fi
    "Horror": [27, 53],            # Horror, Thriller
    "Romance": [10749, 18],        # Romance, Drama
}


TYPE_MAP = {
    "Film": "movie",
    "Serie": "tv"
}


def normalize_label(label: str) -> str:
    """
    Rimuove emoji e prende solo la prima parola.
    Es: 'Azione 💥' → 'Azione'
    """
    return label.split()[0].capitalize()


def convert_moods_to_genre_ids(selected_moods: list[str]) -> list[int]:
    """
    Converte mood selezionati in lista di genre IDs TMDB
    """
    genres = set()

    for mood in selected_moods:
        normalized = normalize_label(mood)
        mapped = MOOD_TO_GENRES.get(normalized)
        if mapped:
            genres.update(mapped)

    return list(genres)


def convert_type(selected_type: str | None) -> str | None:
    """
    Converte tipo utente nel valore TMDB (movie/tv)
    """
    if not selected_type:
        return None

    normalized = normalize_label(selected_type)
    return TYPE_MAP.get(normalized)


def build_genres_param(genre_ids: list[int]) -> str:
    """
    Costruisce la stringa per TMDB:
    [28, 35] → "28,35"
    """
    return ",".join(map(str, genre_ids))