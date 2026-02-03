#!/usr/bin/env python3
"""Validate SLD topology YAML files.

This script validates SLD topology files against the schema and checks
for reference integrity (all parent_bus and connection references exist).

Usage:
    python validate_sld.py sld-topology.yaml
    python validate_sld.py --strict sld-topology.yaml
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


def validate_topology(topology: dict, strict: bool = False) -> tuple[list[str], list[str]]:
    """Validate topology structure and references.

    Args:
        topology: Topology dictionary to validate
        strict: If True, treat warnings as errors

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []

    # Check required fields
    if "metadata" not in topology:
        errors.append("Missing required field: metadata")
    else:
        meta = topology["metadata"]
        if "project_name" not in meta:
            errors.append("Missing required field: metadata.project_name")

    # Collect all IDs
    bus_ids = set()
    eq_ids = set()

    # Validate buses
    for i, bus in enumerate(topology.get("buses", [])):
        if "id" not in bus:
            errors.append(f"Bus at index {i} missing required field: id")
            continue

        bus_id = bus["id"]
        if bus_id in bus_ids:
            errors.append(f"Duplicate bus id: {bus_id}")
        bus_ids.add(bus_id)

        if "bus_type" not in bus:
            errors.append(f"Bus '{bus_id}' missing required field: bus_type")
        if "voltage" not in bus:
            errors.append(f"Bus '{bus_id}' missing required field: voltage")

    # Validate equipment
    for i, eq in enumerate(topology.get("equipment", [])):
        if "id" not in eq:
            errors.append(f"Equipment at index {i} missing required field: id")
            continue

        eq_id = eq["id"]
        if eq_id in eq_ids:
            errors.append(f"Duplicate equipment id: {eq_id}")
        if eq_id in bus_ids:
            errors.append(f"Equipment id '{eq_id}' conflicts with bus id")
        eq_ids.add(eq_id)

        if "equipment_type" not in eq:
            errors.append(f"Equipment '{eq_id}' missing required field: equipment_type")

        # Check parent_bus reference
        parent = eq.get("parent_bus")
        if parent and parent not in bus_ids:
            errors.append(f"Equipment '{eq_id}' references unknown bus '{parent}'")

    all_ids = bus_ids | eq_ids

    # Validate connections
    for i, conn in enumerate(topology.get("connections", [])):
        if "source" not in conn:
            errors.append(f"Connection at index {i} missing required field: source")
        elif conn["source"] not in all_ids:
            errors.append(f"Connection source '{conn['source']}' not found in topology")

        if "target" not in conn:
            errors.append(f"Connection at index {i} missing required field: target")
        elif conn["target"] not in all_ids:
            errors.append(f"Connection target '{conn['target']}' not found in topology")

    # Check for orphaned equipment (no parent_bus and not standalone)
    standalone_types = {"Utility", "Generator", "Transformer", "ATS", "MTS"}
    for eq in topology.get("equipment", []):
        eq_type = eq.get("equipment_type", "")
        if not eq.get("parent_bus") and eq_type not in standalone_types:
            warnings.append(f"Equipment '{eq['id']}' has no parent_bus (orphaned)")

    # Check for buses with no feeders
    buses_with_feeders = set()
    for conn in topology.get("connections", []):
        if conn.get("target") in bus_ids:
            buses_with_feeders.add(conn["target"])
        # Also check for equipment on buses
        for eq in topology.get("equipment", []):
            if eq.get("parent_bus"):
                buses_with_feeders.add(eq["parent_bus"])

    for bus_id in bus_ids:
        if bus_id not in buses_with_feeders:
            warnings.append(f"Bus '{bus_id}' has no incoming feeders or equipment")

    return errors, warnings


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate SLD topology YAML files"
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Topology YAML file to validate",
    )
    parser.add_argument(
        "--strict",
        "-s",
        action="store_true",
        help="Treat warnings as errors",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only output errors, not summary",
    )

    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Load topology
    try:
        with open(args.file) as f:
            topology = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(topology, dict):
        print("Error: Topology must be a YAML mapping", file=sys.stderr)
        sys.exit(1)

    # Validate
    errors, warnings = validate_topology(topology, args.strict)

    # Output results
    if errors:
        print("Errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)

    if warnings and not args.quiet:
        print("Warnings:", file=sys.stderr)
        for warn in warnings:
            print(f"  - {warn}", file=sys.stderr)

    # Summary
    if not args.quiet:
        buses = len(topology.get("buses", []))
        equipment = len(topology.get("equipment", []))
        connections = len(topology.get("connections", []))
        print(f"\nSummary: {buses} buses, {equipment} equipment, {connections} connections")

    # Exit code
    if errors or (args.strict and warnings):
        sys.exit(1)

    if not args.quiet:
        print("\nValidation passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
