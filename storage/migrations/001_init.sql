CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL, subject TEXT DEFAULT '', tags TEXT DEFAULT '',
    notes TEXT DEFAULT '', name TEXT DEFAULT '', company TEXT DEFAULT '',
    line1 TEXT DEFAULT '', line2 TEXT DEFAULT '', city TEXT DEFAULT '',
    state TEXT DEFAULT '', postal_code TEXT DEFAULT '',
    postal_code_plus4 TEXT DEFAULT '', country TEXT DEFAULT 'US',
    phone TEXT DEFAULT '', email TEXT DEFAULT '',
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE, output_mode TEXT NOT NULL,
    envelope_width_in REAL NOT NULL, envelope_height_in REAL NOT NULL,
    logo_path TEXT DEFAULT '', show_logo INTEGER NOT NULL DEFAULT 0,
    return_x REAL NOT NULL DEFAULT 0.45, return_y REAL NOT NULL DEFAULT 0.35,
    to_x REAL NOT NULL DEFAULT 3.2, to_y REAL NOT NULL DEFAULT 2.15,
    font_name TEXT NOT NULL DEFAULT 'Helvetica', font_size INTEGER NOT NULL DEFAULT 11,
    include_stamp_box INTEGER NOT NULL DEFAULT 1, include_subject INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,
    mode TEXT NOT NULL, source_file TEXT DEFAULT '', output_file TEXT DEFAULT '',
    total_rows INTEGER NOT NULL DEFAULT 0, success_rows INTEGER NOT NULL DEFAULT 0,
    failed_rows INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'pending',
    notes TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS job_rows (
    id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER NOT NULL,
    row_number INTEGER NOT NULL, recipient_label TEXT DEFAULT '',
    status TEXT NOT NULL, error_message TEXT DEFAULT '',
    original_address_json TEXT DEFAULT '', corrected_address_json TEXT DEFAULT '',
    quote_json TEXT DEFAULT '', output_path TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    FOREIGN KEY(job_id) REFERENCES jobs(id)
);
CREATE TABLE IF NOT EXISTS address_corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL DEFAULT 'USPS',
    original_address_json TEXT NOT NULL, suggested_address_json TEXT NOT NULL,
    accepted INTEGER, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS app_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
