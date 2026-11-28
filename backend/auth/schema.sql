CREATE TABLE IF NOT EXISTS verification_tokens (
    token_hash TEXT PRIMARY KEY NOT NULL,
    email TEXT NOT NULL COLLATE NOCASE,
    created_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL,
    consumed_at INTEGER,
    client_ip TEXT,

    CHECK (length(token_hash) = 64),
    CHECK (expires_at > created_at),
    CHECK (consumed_at IS NULL OR consumed_at >= created_at)
);

CREATE INDEX IF NOT EXISTS idx_verification_email
    ON verification_tokens(email, created_at);

CREATE INDEX IF NOT EXISTS idx_verification_expiration
    ON verification_tokens(expires_at);


CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY NOT NULL,
    email TEXT NOT NULL COLLATE NOCASE,
    created_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL,
    revoked_at INTEGER,

    CHECK (length(token_hash) = 64),
    CHECK (expires_at > created_at),
    CHECK (revoked_at IS NULL OR revoked_at >= created_at)
);

CREATE INDEX IF NOT EXISTS idx_sessions_email
    ON sessions(email);

CREATE INDEX IF NOT EXISTS idx_sessions_expiration
    ON sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_verification_ip
    ON verification_tokens(client_ip, created_at);

CREATE INDEX IF NOT EXISTS idx_verification_created
    ON verification_tokens(created_at);
