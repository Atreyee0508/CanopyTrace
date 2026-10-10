"""Seed script to build and populate SQLite database from JSON/YAML reference files."""

import json
from pathlib import Path
from typing import Optional
import yaml

from canopytrace.db.database import get_db_connection, init_db, DEFAULT_DB_PATH

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"


def seed_database(db_path: Optional[Path] = None, data_dir: Optional[Path] = None) -> None:
    """Populates SQLite database from JSON/YAML sources."""
    path = db_path or DEFAULT_DB_PATH
    source_dir = data_dir or DATA_DIR

    init_db(path)
    conn = get_db_connection(path)
    cur = conn.cursor()

    # Clear existing seed data
    cur.execute("DELETE FROM range_states;")
    cur.execute("DELETE FROM cites_taxa;")
    cur.execute("DELETE FROM morphology_rules;")
    cur.execute("DELETE FROM smuggling_patterns;")
    cur.execute("DELETE FROM taxa_fts;")

    # 1. Seed CITES Appendices
    cites_file = source_dir / "cites_appendices.json"
    if cites_file.exists():
        with open(cites_file, "r", encoding="utf-8") as f:
            cites_data = json.load(f)
            for item in cites_data:
                cur.execute("""
                    INSERT INTO cites_taxa (
                        scientific_name, common_names, class, order_name, family,
                        appendix, commercial_status, annotations, listing_year
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item["scientific_name"],
                    json.dumps(item.get("common_names", [])),
                    item.get("class"),
                    item.get("order"),
                    item.get("family"),
                    item.get("appendix", "None"),
                    item.get("commercial_status", "UNREGULATED"),
                    item.get("annotations", ""),
                    item.get("listing_year"),
                ))
                # Populate FTS5
                cur.execute("""
                    INSERT INTO taxa_fts (scientific_name, common_names, family)
                    VALUES (?, ?, ?)
                """, (
                    item["scientific_name"],
                    " ".join(item.get("common_names", [])),
                    item.get("family", "")
                ))

    # 2. Seed IUCN Range States
    range_file = source_dir / "iucn_range_states.json"
    if range_file.exists():
        with open(range_file, "r", encoding="utf-8") as f:
            range_data = json.load(f)
            for sci_name, country_codes in range_data.items():
                for code in country_codes:
                    cur.execute("""
                        INSERT OR IGNORE INTO range_states (scientific_name, country_code)
                        VALUES (?, ?)
                    """, (sci_name, code))

    # 3. Seed Morphology Identification Keys
    morph_file = source_dir / "morphology_keys.yaml"
    if morph_file.exists():
        with open(morph_file, "r", encoding="utf-8") as f:
            morph_data = yaml.safe_load(f)
            for key_group in morph_data.get("morphology_keys", []):
                domain = key_group["domain"]
                key_id = key_group["key_id"]
                target_taxa = json.dumps(key_group.get("target_taxa", []))
                confidence = key_group.get("diagnostic_confidence", 1.0)
                rec_lab = key_group.get("recommended_lab_test", "")

                for rule in key_group.get("diagnostic_rules", []):
                    cur.execute("""
                        INSERT INTO morphology_rules (
                            domain, key_id, feature, operator, threshold_json,
                            unit, description, confidence, recommended_lab_test, target_taxa
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        domain,
                        key_id,
                        rule["feature"],
                        rule["operator"],
                        json.dumps(rule["threshold"]),
                        rule.get("unit"),
                        rule.get("description", ""),
                        confidence,
                        rec_lab,
                        target_taxa,
                    ))

    # 4. Seed Smuggling Modus Operandi Patterns
    patterns_file = source_dir / "smuggling_patterns.yaml"
    if patterns_file.exists():
        with open(patterns_file, "r", encoding="utf-8") as f:
            patterns_data = yaml.safe_load(f)
            for mo in patterns_data.get("smuggling_patterns", []):
                cur.execute("""
                    INSERT INTO smuggling_patterns (
                        id, name, category, description, target_contraband,
                        manifest_keywords, physical_indicators, risk_weight,
                        cites_appendix_breach, recommended_lab_assays
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    mo["id"],
                    mo["name"],
                    mo["category"],
                    mo["description"],
                    mo["target_contraband"],
                    json.dumps(mo.get("triggers", {}).get("manifest_keywords", [])),
                    json.dumps(mo.get("triggers", {}).get("physical_indicators", [])),
                    mo.get("risk_weight", 0.5),
                    mo.get("cites_appendix_breach", "I"),
                    json.dumps(mo.get("recommended_lab_assays", [])),
                ))

    conn.commit()
    conn.close()
    print(f"Database seeded successfully at: {path}")


if __name__ == "__main__":
    seed_database()
