"""Higher Authority verification and database learning update hook."""

import json
from pathlib import Path
from typing import List, Optional

from canopytrace.db import get_db_connection, insert_verified_species
from canopytrace.escalation.queue import DEFAULT_ESCALATION_DIR


def approve_and_ingest_novel_finding(
    case_id: str,
    verified_species: str,
    verified_appendix: str,
    authority_notes: str,
    common_names: Optional[List[str]] = None,
    commercial_status: str = "BANNED",
    range_countries: Optional[List[str]] = None,
    escalation_dir: Optional[Path] = None,
    db_path: Optional[Path] = None,
) -> bool:
    """
    Approves an escalated anomaly case and updates the offline SQLite database so future
    inspections immediately recognize the newly identified species or pattern.
    """
    common_list = common_names or [verified_species]
    countries_list = range_countries or ["ALL"]

    # 1. Update SQLite reference database with verified finding
    insert_verified_species(
        scientific_name=verified_species,
        common_names=common_list,
        appendix=verified_appendix,
        commercial_status=commercial_status,
        annotations=authority_notes,
        range_countries=countries_list,
        db_path=db_path,
    )

    # 2. Update escalation record in database
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        UPDATE escalation_records
        SET status = 'APPROVED',
            authority_review_notes = ?,
            verified_species = ?,
            verified_appendix = ?,
            updated_database = 1
        WHERE case_id = ?
    """, (authority_notes, verified_species, verified_appendix, case_id))
    conn.commit()
    conn.close()

    # 3. Update file on disk if present
    target_dir = escalation_dir or DEFAULT_ESCALATION_DIR
    file_path = target_dir / f"{case_id}.json"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["status"] = "APPROVED"
        data["authority_review_notes"] = authority_notes
        data["verified_species"] = verified_species
        data["verified_appendix"] = verified_appendix
        data["updated_database"] = True
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    return True
