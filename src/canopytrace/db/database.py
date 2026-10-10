"""SQLite reference database connection, schema setup, and query operations."""

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

if os.environ.get("CANOPYTRACE_DB_PATH"):
    DEFAULT_DB_PATH = Path(os.environ["CANOPYTRACE_DB_PATH"])
elif os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    DEFAULT_DB_PATH = Path("/tmp/canopytrace/data/reference.db")
else:
    DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "reference.db"


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Returns a connection to the SQLite reference database with WAL mode and row factory."""
    path = db_path or (Path(os.environ["CANOPYTRACE_DB_PATH"]) if os.environ.get("CANOPYTRACE_DB_PATH") else DEFAULT_DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
    except Exception:
        pass
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
    except Exception:
        pass
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    """Initializes SQLite schema tables, indexes, and FTS5 full-text search."""
    conn = get_db_connection(db_path)
    cur = conn.cursor()

    cur.executescript("""
    -- CITES taxonomy and protection status
    CREATE TABLE IF NOT EXISTS cites_taxa (
        scientific_name TEXT PRIMARY KEY,
        common_names TEXT NOT NULL,       -- JSON array of strings
        class TEXT,
        order_name TEXT,
        family TEXT,
        appendix TEXT NOT NULL,           -- 'I', 'II', 'III', or 'None'
        commercial_status TEXT NOT NULL,  -- 'BANNED', 'QUOTA_CONTROLLED', 'UNREGULATED'
        annotations TEXT,
        listing_year INTEGER
    );

    CREATE INDEX IF NOT EXISTS idx_cites_appendix ON cites_taxa(appendix);

    -- IUCN and native geographic distribution states
    CREATE TABLE IF NOT EXISTS range_states (
        scientific_name TEXT NOT NULL,
        country_code TEXT NOT NULL,       -- ISO 2-letter code or 'ALL'
        PRIMARY KEY (scientific_name, country_code),
        FOREIGN KEY (scientific_name) REFERENCES cites_taxa(scientific_name) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_range_country ON range_states(country_code);

    -- Morphology rules and identification keys
    CREATE TABLE IF NOT EXISTS morphology_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT NOT NULL,             -- 'ivory', 'timber', 'keratin_scales', etc.
        key_id TEXT NOT NULL,
        feature TEXT NOT NULL,
        operator TEXT NOT NULL,           -- 'gt', 'lt', 'eq', 'between', 'in'
        threshold_json TEXT NOT NULL,     -- JSON encoded threshold value
        unit TEXT,
        description TEXT,
        confidence REAL DEFAULT 1.0,
        recommended_lab_test TEXT,
        target_taxa TEXT NOT NULL         -- JSON array of scientific names
    );

    CREATE INDEX IF NOT EXISTS idx_morph_domain ON morphology_rules(domain);
    CREATE INDEX IF NOT EXISTS idx_morph_feature ON morphology_rules(feature);

    -- Documented wildlife trafficking modus operandi (MOs)
    CREATE TABLE IF NOT EXISTS smuggling_patterns (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        target_contraband TEXT NOT NULL,
        manifest_keywords TEXT NOT NULL,  -- JSON array of keywords
        physical_indicators TEXT NOT NULL,-- JSON array of conditions
        risk_weight REAL NOT NULL,
        cites_appendix_breach TEXT NOT NULL,
        recommended_lab_assays TEXT NOT NULL -- JSON array of assays
    );

    -- Scientific authority escalation cases
    CREATE TABLE IF NOT EXISTS escalation_records (
        case_id TEXT PRIMARY KEY,
        escalation_id TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        checkpoint_location TEXT NOT NULL,
        manifest_summary TEXT NOT NULL,
        observed_measurements TEXT NOT NULL,
        reason TEXT NOT NULL,
        status TEXT NOT NULL,
        authority_review_notes TEXT,
        verified_species TEXT,
        verified_appendix TEXT,
        updated_database INTEGER DEFAULT 0
    );

    -- Full-text search index for fuzzy matching of trade terms
    CREATE VIRTUAL TABLE IF NOT EXISTS taxa_fts USING fts5(
        scientific_name,
        common_names,
        family,
        tokenize = 'unicode61'
    );
    """)

    conn.commit()
    conn.close()


def query_cites_by_name(query: str, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """
    Looks up a taxon by exact scientific name, common name, or keyword token search via FTS5/LIKE.
    """
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    q = query.strip()

    # 1. Exact scientific name query
    cur.execute("SELECT * FROM cites_taxa WHERE LOWER(scientific_name) = LOWER(?)", (q,))
    row = cur.fetchone()
    if row:
        res = dict(row)
        res["common_names"] = json.loads(res["common_names"])
        conn.close()
        return res

    # 2. Substring match across common_names JSON string or scientific_name
    cur.execute("""
        SELECT * FROM cites_taxa
        WHERE LOWER(common_names) LIKE ? OR LOWER(scientific_name) LIKE ?
        LIMIT 1
    """, (f"%{q.lower()}%", f"%{q.lower()}%"))
    row = cur.fetchone()
    if row:
        res = dict(row)
        res["common_names"] = json.loads(res["common_names"])
        conn.close()
        return res

    # 3. Individual token search (e.g. 'Mammoth' from 'Antique Mammoth Carvings')
    tokens = [t.lower() for t in q.split() if len(t) > 3]
    for token in tokens:
        cur.execute("""
            SELECT * FROM cites_taxa
            WHERE LOWER(common_names) LIKE ? OR LOWER(scientific_name) LIKE ?
            LIMIT 1
        """, (f"%{token}%", f"%{token}%"))
        row = cur.fetchone()
        if row:
            res = dict(row)
            res["common_names"] = json.loads(res["common_names"])
            conn.close()
            return res

    # 4. FTS5 fallback
    for token in tokens:
        try:
            cur.execute("""
                SELECT c.* FROM cites_taxa c
                JOIN taxa_fts f ON c.scientific_name = f.scientific_name
                WHERE taxa_fts MATCH ?
                LIMIT 1
            """, (f'"{token}"*',))
            row = cur.fetchone()
            if row:
                res = dict(row)
                res["common_names"] = json.loads(res["common_names"])
                conn.close()
                return res
        except Exception:
            pass

    conn.close()
    return None


def is_in_range_state(scientific_name: str, country_code: str, db_path: Optional[Path] = None) -> bool:
    """Checks if a country code is a recognized native range state for the taxon."""
    conn = get_db_connection(db_path)
    cur = conn.cursor()

    code = country_code.strip().upper()
    cur.execute("""
        SELECT 1 FROM range_states
        WHERE LOWER(scientific_name) = LOWER(?)
          AND (country_code = ? OR country_code = 'ALL')
        LIMIT 1
    """, (scientific_name.strip(), code))
    match = cur.fetchone() is not None
    conn.close()
    return match


def get_range_states(scientific_name: str, db_path: Optional[Path] = None) -> List[str]:
    """Retrieves all registered range state ISO codes for a taxon."""
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT country_code FROM range_states WHERE LOWER(scientific_name) = LOWER(?)", (scientific_name.strip(),))
    rows = cur.fetchall()
    conn.close()
    return [r["country_code"] for r in rows]


def get_morphology_rules(domain: Optional[str] = None, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Retrieves morphology rules filtered by domain or all rules."""
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    if domain:
        cur.execute("SELECT * FROM morphology_rules WHERE domain = ?", (domain,))
    else:
        cur.execute("SELECT * FROM morphology_rules")
    rows = cur.fetchall()
    conn.close()

    results = []
    for r in rows:
        item = dict(r)
        item["threshold"] = json.loads(item["threshold_json"])
        item["target_taxa"] = json.loads(item["target_taxa"])
        results.append(item)
    return results


def get_all_smuggling_patterns(db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Retrieves all registered smuggling patterns."""
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM smuggling_patterns")
    rows = cur.fetchall()
    conn.close()

    results = []
    for r in rows:
        item = dict(r)
        item["manifest_keywords"] = json.loads(item["manifest_keywords"])
        item["physical_indicators"] = json.loads(item["physical_indicators"])
        item["recommended_lab_assays"] = json.loads(item["recommended_lab_assays"])
        results.append(item)
    return results


def insert_verified_species(
    scientific_name: str,
    common_names: List[str],
    appendix: str,
    commercial_status: str,
    annotations: str,
    range_countries: List[str],
    db_path: Optional[Path] = None,
) -> None:
    """Inserts an authority-verified taxon into the offline reference database."""
    conn = get_db_connection(db_path)
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO cites_taxa
        (scientific_name, common_names, appendix, commercial_status, annotations)
        VALUES (?, ?, ?, ?, ?)
    """, (
        scientific_name,
        json.dumps(common_names),
        appendix,
        commercial_status,
        annotations,
    ))

    # Update FTS5
    cur.execute("DELETE FROM taxa_fts WHERE scientific_name = ?", (scientific_name,))
    cur.execute("""
        INSERT INTO taxa_fts (scientific_name, common_names, family)
        VALUES (?, ?, '')
    """, (scientific_name, " ".join(common_names)))

    # Insert range states
    for c in range_countries:
        cur.execute("""
            INSERT OR IGNORE INTO range_states (scientific_name, country_code)
            VALUES (?, ?)
        """, (scientific_name, c.upper()))

    conn.commit()
    conn.close()
