CREATE TABLE IF NOT EXISTS users (
    user_id           TEXT PRIMARY KEY,
    genre_weights     JSONB DEFAULT '{}',
    mood_history      JSONB DEFAULT '[]',
    seen_ids          JSONB DEFAULT '[]',
    selezioni         JSONB DEFAULT '{}',
    sessione_corrente JSONB DEFAULT '{}',
    creato_il         TIMESTAMP DEFAULT NOW(),
    aggiornato_il     TIMESTAMP DEFAULT NOW()
);

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
);
