from config import BASE_URL
import httpx
from config import TMDB_API_KEY

async def search_movies(type_: str | None = "movie", genres: list[int] | None = None) -> list[dict]:
    """
    Cerca film/serie su TMDb usando type_ e lista di genre IDs
    """
    if not type_:
        type_ = "movie"

    genre_param = ",".join(map(str, genres)) if genres else None

    url = f"{BASE_URL}/{type_}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "it-IT",
        "sort_by": "popularity.desc",
        "with_genres": genre_param,
        "page": 1
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("results", [])
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"Errore TMDb: {e}")
            return []