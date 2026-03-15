BOOST_MAX = 1.5
BOOST_MIN = 0.5
TOP_GENERI_COUNT = 3


async def init_db(db) -> None:
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id           TEXT PRIMARY KEY,
            genre_weights     JSONB DEFAULT '{}',
            mood_history      JSONB DEFAULT '[]',
            seen_ids          JSONB DEFAULT '[]',
            selezioni         JSONB DEFAULT '{}',
            sessione_corrente JSONB DEFAULT '{}',
            creato_il         TIMESTAMP DEFAULT NOW(),
            aggiornato_il     TIMESTAMP DEFAULT NOW()
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id          SERIAL PRIMARY KEY,
            user_id     TEXT REFERENCES users(user_id),
            film_id     INTEGER NOT NULL,
            titolo      TEXT NOT NULL,
            anno        INTEGER,
            generi      JSONB DEFAULT '[]',
            voto        FLOAT,
            piattaforma TEXT,
            aggiunto_il TIMESTAMP DEFAULT NOW(),
            UNIQUE(user_id, film_id)
        )
    """)


async def _ensure_user(db, user_id: int) -> None:
    await db.execute(
        "INSERT INTO users (user_id) VALUES ($1) ON CONFLICT DO NOTHING",
        str(user_id),
    )


async def get_user_selections(db, user_id: int, category: str) -> set:
    row = await db.fetchrow("SELECT selezioni FROM users WHERE user_id = $1", str(user_id))
    if not row:
        return set()
    selezioni = row["selezioni"] or {}
    return set(selezioni.get(category, []))


async def set_user_selection(db, user_id: int, category: str, selections: set) -> None:
    await _ensure_user(db, user_id)
    await db.execute(
        """
        UPDATE users
        SET selezioni = jsonb_set(
            COALESCE(selezioni, '{}'),
            $2::text[],
            $3::jsonb
        ),
        aggiornato_il = NOW()
        WHERE user_id = $1
        """,
        str(user_id),
        [category],
        list(selections),
    )


async def clear_user(db, user_id: int) -> None:
    await _ensure_user(db, user_id)
    await db.execute(
        """
        UPDATE users
        SET selezioni = '{}', sessione_corrente = '{}'
        WHERE user_id = $1
        """,
        str(user_id),
    )


async def get_profilo_utente(db, user_id: int) -> dict:
    row = await db.fetchrow(
        "SELECT genre_weights, seen_ids FROM users WHERE user_id = $1",
        str(user_id),
    )
    if not row:
        return {"genre_weights": {}, "seen_ids": []}
    return {
        "genre_weights": row["genre_weights"] or {},
        "seen_ids": row["seen_ids"] or [],
    }


async def salva_feedback(db, user_id: int, film_id: int, genre_ids: list[int], like: bool) -> None:
    await _ensure_user(db, user_id)
    row = await db.fetchrow(
        "SELECT genre_weights, seen_ids FROM users WHERE user_id = $1",
        str(user_id),
    )
    genre_weights = dict(row["genre_weights"] or {})
    seen_ids = list(row["seen_ids"] or [])

    delta = 0.1 if like else -0.1
    for genre_id in genre_ids:
        key = str(genre_id)
        current = float(genre_weights.get(key, 1.0))
        genre_weights[key] = max(BOOST_MIN, min(BOOST_MAX, current + delta))

    if film_id not in seen_ids:
        seen_ids.append(film_id)

    await db.execute(
        """
        UPDATE users
        SET genre_weights = $2, seen_ids = $3, aggiornato_il = NOW()
        WHERE user_id = $1
        """,
        str(user_id),
        genre_weights,
        seen_ids,
    )


async def salva_sessione(db, user_id: int, mood: str, piattaforme: list[str], tipo_api: str, film: dict) -> None:
    await _ensure_user(db, user_id)
    anno_raw = (film.get("release_date") or film.get("first_air_date") or "")[:4]
    sessione = {
        "mood": mood,
        "piattaforme": piattaforme,
        "tipo_api": tipo_api,
        "ultimo_film_id": film["id"],
        "ultimo_film_genres": film.get("genre_ids", []),
        "ultimo_film_titolo": film.get("title") or film.get("name", "N/A"),
        "ultimo_film_anno": int(anno_raw) if anno_raw.isdigit() else 0,
        "ultimo_film_voto": film.get("vote_average"),
    }
    row = await db.fetchrow("SELECT mood_history FROM users WHERE user_id = $1", str(user_id))
    mood_history = list(row["mood_history"] or []) if row else []
    mood_history.append(mood)

    await db.execute(
        """
        UPDATE users
        SET sessione_corrente = $2, mood_history = $3, aggiornato_il = NOW()
        WHERE user_id = $1
        """,
        str(user_id),
        sessione,
        mood_history,
    )


async def get_sessione(db, user_id: int) -> dict:
    row = await db.fetchrow("SELECT sessione_corrente FROM users WHERE user_id = $1", str(user_id))
    if not row:
        return {}
    return row["sessione_corrente"] or {}


async def segna_come_visto(db, user_id: int, film_id: int) -> None:
    await _ensure_user(db, user_id)
    row = await db.fetchrow("SELECT seen_ids FROM users WHERE user_id = $1", str(user_id))
    seen_ids = list(row["seen_ids"] or [])
    if film_id not in seen_ids:
        seen_ids.append(film_id)
    await db.execute(
        "UPDATE users SET seen_ids = $2, aggiornato_il = NOW() WHERE user_id = $1",
        str(user_id),
        seen_ids,
    )


async def reset_seen(db, user_id: int) -> None:
    await _ensure_user(db, user_id)
    await db.execute(
        "UPDATE users SET seen_ids = '[]', aggiornato_il = NOW() WHERE user_id = $1",
        str(user_id),
    )


async def aggiungi_watchlist(db, user_id: int, film: dict, piattaforma: str) -> None:
    await _ensure_user(db, user_id)
    await db.execute(
        """
        INSERT INTO watchlist (user_id, film_id, titolo, anno, generi, voto, piattaforma)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (user_id, film_id) DO NOTHING
        """,
        str(user_id),
        film["film_id"],
        film["titolo"],
        film.get("anno") or 0,
        film.get("generi", []),
        film.get("voto"),
        piattaforma,
    )


async def get_watchlist(db, user_id: int) -> list[dict]:
    rows = await db.fetch(
        "SELECT film_id, titolo, anno, generi, voto, piattaforma FROM watchlist WHERE user_id = $1 ORDER BY aggiunto_il",
        str(user_id),
    )
    return [dict(r) for r in rows]


async def rimuovi_watchlist(db, user_id: int, film_id: int) -> None:
    await db.execute(
        "DELETE FROM watchlist WHERE user_id = $1 AND film_id = $2",
        str(user_id),
        film_id,
    )


async def get_stats(db, user_id: int) -> dict:
    from utils.mapper import GENRE_ID_TO_NAME
    row = await db.fetchrow(
        "SELECT genre_weights, seen_ids, mood_history FROM users WHERE user_id = $1",
        str(user_id),
    )
    watchlist_count = await db.fetchval(
        "SELECT COUNT(*) FROM watchlist WHERE user_id = $1",
        str(user_id),
    )

    if not row:
        return {"top_generi": [], "film_visti": 0, "mood_preferito": None, "watchlist_count": 0}

    genre_weights = row["genre_weights"] or {}
    seen_ids = row["seen_ids"] or []
    mood_history = list(row["mood_history"] or [])

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
        "watchlist_count": watchlist_count or 0,
    }
