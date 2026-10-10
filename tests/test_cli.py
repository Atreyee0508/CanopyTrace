"""Integration tests for CanopyTrace CLI commands."""

import json
from pathlib import Path
from click.testing import CliRunner
from canopytrace.cli import main


def test_cli_patterns_list():
    runner = CliRunner()
    result = runner.invoke(main, ["patterns", "list"])
    assert result.exit_code == 0
    assert "MO-IVO-001" in result.output
    assert "Antique Mammoth" in result.output


def test_cli_db_seed():
    runner = CliRunner()
    result = runner.invoke(main, ["db", "seed"])
    assert result.exit_code == 0
    assert "Reference database seeded successfully" in result.output


def test_cli_escalate_list():
    runner = CliRunner()
    result = runner.invoke(main, ["escalate", "list"])
    assert result.exit_code == 0


def test_cli_inspect_command(tmp_path):
    manifest_data = {
        "manifest_id": "CLI-TEST-01",
        "waybill_number": "WB-CLI-100",
        "shipper": "Export Ltd",
        "consignee": "Import Ltd",
        "declared_item_name": "Antique Mammoth Carvings",
        "declared_quantity": 100.0,
        "declared_unit": "kg",
        "country_of_origin": "RU",
        "destination_country": "HK",
    }
    inspection_data = {
        "inspection_id": "INSP-CLI-01",
        "inspector_id": "AGENT-CLI",
        "checkpoint_location": "Hong Kong Port",
        "observed_specimen_category": "ivory",
        "measurements": [
            {"feature_name": "schreger_angle_outer", "value": 125.0, "unit": "degrees"}
        ],
    }

    manifest_file = tmp_path / "manifest.json"
    inspection_file = tmp_path / "inspection.json"

    with open(manifest_file, "w") as f:
        json.dump(manifest_data, f)
    with open(inspection_file, "w") as f:
        json.dump(inspection_data, f)

    runner = CliRunner()
    result = runner.invoke(main, [
        "inspect",
        "--manifest", str(manifest_file),
        "--inspection", str(inspection_file),
        "--case-id", "CASE-CLI-TEST",
        "--outdir", str(tmp_path / "output")
    ])

    assert result.exit_code == 0
    assert "CASE-CLI-TEST" in result.output
    assert "Discrepancy Score" in result.output
    assert "CRITICAL SEIZURE ALERT" in result.output
    assert "SHA-256 Digest" in result.output
