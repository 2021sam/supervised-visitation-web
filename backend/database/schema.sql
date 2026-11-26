CREATE TABLE IF NOT EXISTS supervisors (
    supervisor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    website TEXT NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    state_code TEXT NOT NULL DEFAULT '',
    zip_code TEXT NOT NULL DEFAULT '',
    latitude REAL,
    longitude REAL
);

CREATE TABLE IF NOT EXISTS supervisor_courts (
    supervisor_id INTEGER NOT NULL
        REFERENCES supervisors(supervisor_id),
    state_code TEXT NOT NULL,
    county TEXT NOT NULL,
    court_url TEXT NOT NULL DEFAULT '',
    source_url TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (supervisor_id, state_code, county)
);

CREATE INDEX IF NOT EXISTS idx_supervisors_location
ON supervisors(state_code, city, zip_code);

CREATE INDEX IF NOT EXISTS idx_supervisor_courts_location
ON supervisor_courts(state_code, county);

CREATE TABLE IF NOT EXISTS supervisor_sources (
    source_system TEXT NOT NULL,
    source_id INTEGER NOT NULL,
    supervisor_id INTEGER NOT NULL
        REFERENCES supervisors(supervisor_id),
    PRIMARY KEY (source_system, source_id)
);

CREATE INDEX IF NOT EXISTS idx_supervisor_sources_supervisor
ON supervisor_sources(supervisor_id);
