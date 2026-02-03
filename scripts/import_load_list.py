#!/usr/bin/env python3
"""Import load list data for SLD generation.

This script provides utilities for parsing load-list-skill output
and extracting data needed for SLD topology generation.

Usage:
    python import_load_list.py --input load-list.yaml --output sld-topology.yaml

The MCP server's sld_bootstrap_from_loadlist tool provides the same
functionality with more options.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


def parse_load_list(file_path: Path) -> dict[str, Any]:
    """Parse load list YAML file.

    Args:
        file_path: Path to load-list.yaml

    Returns:
        Parsed load list dictionary
    """
    with open(file_path) as f:
        return yaml.safe_load(f)


def extract_electrical_basis(load_list: dict) -> dict:
    """Extract electrical basis information.

    Args:
        load_list: Parsed load list

    Returns:
        Electrical basis dictionary
    """
    basis = load_list.get("electrical_basis", {})
    return {
        "code_basis": basis.get("code_basis", {}).get("standard", "IEC"),
        "motor_standard": basis.get("motor_standard", "IEC"),
        "voltage_system": basis.get("voltage_system", {}),
        "fault_current": basis.get("available_fault_current", {}),
    }


def extract_panels(load_list: dict) -> list[dict]:
    """Extract MCC panel information.

    Args:
        load_list: Parsed load list

    Returns:
        List of panel dictionaries
    """
    return load_list.get("mcc_panels", [])


def extract_loads(load_list: dict) -> list[dict]:
    """Extract load/equipment information.

    Args:
        load_list: Parsed load list

    Returns:
        List of load dictionaries
    """
    return load_list.get("loads", [])


def get_output_tier(load_list: dict) -> dict:
    """Get output tier information.

    Args:
        load_list: Parsed load list

    Returns:
        Output tier dictionary with tier level and disclaimers
    """
    return load_list.get("output_tier", {"tier": 1})


def summarize_load_list(load_list: dict) -> dict:
    """Generate summary of load list data.

    Args:
        load_list: Parsed load list

    Returns:
        Summary dictionary
    """
    panels = extract_panels(load_list)
    loads = extract_loads(load_list)
    tier = get_output_tier(load_list)
    energy = load_list.get("energy_summary", {})

    return {
        "project_id": load_list.get("project_id", "Unknown"),
        "tier": tier.get("tier", 1),
        "tier_name": tier.get("tier_name", "Load Study"),
        "panel_count": len(panels),
        "load_count": len(loads),
        "total_connected_kw": energy.get("total_connected_kw", 0),
        "total_demand_kw": energy.get("total_demand_kw", 0),
        "feeder_types": _count_feeder_types(loads),
    }


def _count_feeder_types(loads: list[dict]) -> dict[str, int]:
    """Count loads by feeder type."""
    counts: dict[str, int] = {}
    for load in loads:
        feeder = load.get("feeder_type", "DOL")
        counts[feeder] = counts.get(feeder, 0) + 1
    return counts


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Import load list data for SLD generation"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        required=True,
        help="Path to load-list.yaml",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output path for extracted data (optional)",
    )
    parser.add_argument(
        "--summary",
        "-s",
        action="store_true",
        help="Print summary only",
    )

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    load_list = parse_load_list(args.input)

    if args.summary:
        summary = summarize_load_list(load_list)
        print(yaml.dump(summary, default_flow_style=False))
        return

    # Extract key data
    data = {
        "electrical_basis": extract_electrical_basis(load_list),
        "panels": extract_panels(load_list),
        "loads": extract_loads(load_list),
        "output_tier": get_output_tier(load_list),
    }

    if args.output:
        with open(args.output, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
        print(f"Extracted data saved to: {args.output}")
    else:
        print(yaml.dump(data, default_flow_style=False))


if __name__ == "__main__":
    main()
