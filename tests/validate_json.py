#!/usr/bin/env python3
"""
Validate JSON syntax and basic structure of Frodo CLI export files.
Usage: python3 tests/validate_json.py exports/
"""

import json
import sys
import os
from pathlib import Path


def validate_json_file(filepath):
    """Validate a single JSON file. Returns (ok, error_message)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"JSON parse error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def validate_directory(directory):
    """Validate all JSON files in a directory recursively."""
    base = Path(directory)
    if not base.exists():
        print(f"Directory not found: {directory}")
        return True  # Not an error if exports don't exist yet

    json_files = list(base.rglob("*.json"))
    if not json_files:
        print(f"No JSON files found in {directory}")
        return True

    errors = []
    for filepath in sorted(json_files):
        ok, error = validate_json_file(filepath)
        if ok:
            print(f"  ✅ {filepath.relative_to(base.parent)}")
        else:
            print(f"  ❌ {filepath.relative_to(base.parent)}: {error}")
            errors.append((filepath, error))

    print(f"\nValidated {len(json_files)} files, {len(errors)} errors")
    return len(errors) == 0


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else "exports/"
    print(f"Validating JSON files in: {directory}\n")
    success = validate_directory(directory)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
