#!/usr/bin/env python3
"""
Standalone runner script and module for the case-dossier-compiler skill.
Complies with agentskills.io standard.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from canopytrace.dossier import compile_evidentiary_dossier


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile multi-format tamper-evident case dossier.")
    parser.add_argument("--case-file", required=True, help="Path to aggregated case JSON file.")
    parser.add_argument("--outdir", default="./output", help="Directory where dossier files will be written.")
    args = parser.parse_args()

    with open(args.case_file, "r", encoding="utf-8") as f:
        case_data = json.load(f)

    out_dir = Path(args.outdir)
    res = compile_evidentiary_dossier(case_data, out_dir)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
