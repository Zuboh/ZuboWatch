from datetime import datetime

PLATFORM_TO_ID = {
    "Netflix": 8,
    "Prime Video": 119,
    "Disney+": 337,
    "Apple TV+": 350,
    "Paramount+": 531,
    "NOW": 39,
}

MOOD_TO_GENRES = {
    "Azione": [28, 12, 53],        # Action, Adventure, Thriller
    "Comico": [35],                # Comedy
    "Drammatico": [18, 10749],     # Drama, Romance
    "Riflessivo": [18, 9648, 878], # Drama, Mystery, Sci-Fi
    "Horror": [27, 53],            # Horror, Thriller
    "Romance": [10749, 18],        # Romance, Drama
}


GENRE_ID_TO_NAME: dict[int, str] = {
    12: "Avventura",
    14: "Fantasy",
    16: "Animazione",
    18: "Dramma",
    27: "Horror",
    28: "Azione",
    35: "Commedia",
    36: "Storia",
    37: "Western",
    53: "Thriller",
    80: "Crimine",
    99: "Documentario",
    878: "Fantascienza",
    9648: "Mistero",
    10402: "Musica",
    10749: "Romance",
    10751: "Famiglia",
    10752: "Guerra",
    10770: "Film TV",
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


def convert_platforms_to_provider_ids(platforms: list[str]) -> list[int]:
    return [PLATFORM_TO_ID[p] for p in platforms if p in PLATFORM_TO_ID]


def build_genres_param(genre_ids: list[int]) -> str:
    """
    Costruisce la stringa per TMDB:
    [28, 35] → "28,35"
    """
    return ",".join(map(str, genre_ids))


def genre_ids_to_nomi(ids: list[int]) -> list[str]:
    return [GENRE_ID_TO_NAME[i] for i in ids if i in GENRE_ID_TO_NAME]


def mood_to_genres(mood: str) -> list[int]:
    normalized = normalize_label(mood)
    return MOOD_TO_GENRES.get(normalized, [])


def get_mood_question() -> str:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Che mood hai stamattina?"
    elif 12 <= hour < 18:
        return "Che mood hai questo pomeriggio?"
    elif 18 <= hour < 21:
        return "Che mood hai stasera?"
    else:
        return "Che mood hai stanotte?"