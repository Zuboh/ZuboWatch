from config import BASE_URL, TMDB_API_KEY
import httpx

TMDB_API_BASE = "https://api.themoviedb.org/3"

MIN_VOTE_AVERAGE = 6.5
MIN_VOTE_COUNT = 200


def _filtra_per_qualita(results: list[dict]) -> list[dict]:
    """Filtra client-side per qualità; se troppo restrittivo ritorna tutto."""
    qualita = [
        r for r in results
        if r.get("vote_average", 0) >= MIN_VOTE_AVERAGE
        and r.get("vote_count", 0) >= MIN_VOTE_COUNT
    ]
    return qualita if qualita else results


async def search_movies(
    type_: str | None = "movie",
    genres: list[int] | None = None,
    providers: list[int] | None = None,
) -> list[dict]:
    """Cerca film/serie su TMDb; filtra per qualità lato client con fallback."""
    if not type_:
        type_ = "movie"

    genre_param = "|".join(map(str, genres)) if genres else None

    url = f"{BASE_URL}/{type_}"
    raw_params = {
        "api_key": TMDB_API_KEY,
        "language": "it-IT",
        "sort_by": "popularity.desc",
        "with_genres": genre_param,
        "page": 1,
        "with_watch_providers": ",".join(map(str, providers)) if providers else None,
        "watch_region": "IT" if providers else None,
    }
    params = {k: v for k, v in raw_params.items() if v is not None}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            results = resp.json().get("results", [])
            return _filtra_per_qualita(results)
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"Errore TMDb: {e}")
            return []


async def fetch_candidates(
    tipo: str, moods: list[str], providers: list[int] | None = None
) -> list[dict]:
    from utils.mapper import mood_to_genres
    genres: set[int] = set()
    for mood in moods:
        genres.update(mood_to_genres(mood))
    return await search_movies(type_=tipo, genres=list(genres), providers=providers)


async def get_details(type_: str, id_: int) -> dict:
    url = f"{TMDB_API_BASE}/{type_}/{id_}"
    params = {"api_key": TMDB_API_KEY, "language": "it-IT"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except (httpx.RequestError, httpx.HTTPStatusError):
            return {}


async def get_watch_providers(type_: str, id_: int) -> list[str]:
    url = f"{TMDB_API_BASE}/{type_}/{id_}/watch/providers"
    params = {"api_key": TMDB_API_KEY}
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            it = resp.json().get("results", {}).get("IT", {})
            providers = it.get("flatrate") or it.get("rent") or it.get("buy") or []
            return [p["provider_name"] for p in providers]
        except (httpx.RequestError, httpx.HTTPStatusError):
            return []
