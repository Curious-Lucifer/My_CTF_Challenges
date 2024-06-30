CREATE TABLE IF NOT EXISTS users (
    uid INTEGER PRIMARY KEY AUTOINCREMENT,
    valid_until INTEGER, 
    is_pow_verified INTEGER DEFAULT 0,
    is_running_challenge INTEGER DEFAULT 0, 
    run_until INTEGER DEFAULT 0, 
    has_result INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL UNIQUE,
    valid_until INTEGER,
    prefix TEXT
)
