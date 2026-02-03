#!/usr/bin/env python3
"""Build SLD topology from scratch or customize existing.

This script provides utilities for manually building or modifying
SLD topology YAML files outside of the MCP server.

Usage:
    python build_sld_topology.py --project "My Project" --output sld.yaml
    python build_sld_topology.py --input draft.yaml --validate --output sld.yaml

For most use cases, use the MCP server's sld_bootstrap_from_loadlist tool.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


def create_empty_topology(project_name: str, voltage: str = "400V") -> dict:
    """Create an empty topology structure.

    Args:
        project_name: Project name for metadata
        voltage: Primary LV voltage level

    Returns:
        Empty topology dictionary
    """
    return {
        "schema_version": "1.0",
        "metadata": {
            "project_name": project_name,
            "revision": "A",
            "voltage_system": f"{voltage}/230V 3Ph 4W",
            "frequency": 50,
            "code_basis": "IEC",
        },
        "buses": [],
        "equipment": [],
        "connections": [],
        "view_mode": "detailed",
    }


def add_utility(topology: dict, voltage: str = "11kV") -> dict:
    """Add utility connection to topology.

    Args:
        topology: Existing topology
        voltage: Utility voltage

    Returns:
        Updated topology
    """
    topology["equipment"].append(
        {
            "id": "UTIL-01",
            "equipment_type": "Utility",
            "name": "Utility Supply",
            "voltage": voltage,
        }
    )
    return topology


def add_transformer(
    topology: dict,
    id: str,
    kva: float,
    primary_v: str,
    secondary_v: str,
) -> dict:
    """Add transformer to topology.

    Args:
        topology: Existing topology
        id: Transformer ID
        kva: Rating in kVA
        primary_v: Primary voltage
        secondary_v: Secondary voltage

    Returns:
        Updated topology
    """
    topology["equipment"].append(
        {
            "id": id,
            "equipment_type": "Transformer",
            "name": f"Transformer {id}",
            "rated_kVA": kva,
            "primary_voltage": primary_v,
            "secondary_voltage": secondary_v,
        }
    )
    return topology


def add_bus(
    topology: dict,
    id: str,
    bus_type: str,
    voltage: str,
    name: str = "",
    rated_current: float = 0,
) -> dict:
    """Add bus/switchboard to topology.

    Args:
        topology: Existing topology
        id: Bus ID
        bus_type: Type (Main_Switchboard, MCC, Distribution_Panel)
        voltage: Voltage level
        name: Display name
        rated_current: Bus rating in A

    Returns:
        Updated topology
    """
    topology["buses"].append(
        {
            "id": id,
            "name": name or id,
            "bus_type": bus_type,
            "voltage": voltage,
            "rated_current_A": rated_current,
        }
    )
    return topology


def add_motor(
    topology: dict,
    id: str,
    parent_bus: str,
    kw: float,
    feeder_type: str = "DOL",
    name: str = "",
) -> dict:
    """Add motor to topology.

    Args:
        topology: Existing topology
        id: Motor ID
        parent_bus: Parent bus ID
        kw: Motor rating in kW
        feeder_type: Feeder type (DOL, VFD, Soft-Starter)
        name: Display name

    Returns:
        Updated topology
    """
    eq_type = "Motor"
    if feeder_type == "VFD":
        eq_type = "VFD"
    elif feeder_type in ("Soft-Starter", "SOFT-STARTER"):
        eq_type = "Soft_Starter"

    topology["equipment"].append(
        {
            "id": id,
            "equipment_type": eq_type,
            "name": name or id,
            "rated_kW": kw,
            "parent_bus": parent_bus,
            "feeder_type": feeder_type,
        }
    )
    return topology


def add_connection(
    topology: dict,
    source: str,
    target: str,
    connection_type: str = "Feeder",
    label: str = "",
) -> dict:
    """Add connection to topology.

    Args:
        topology: Existing topology
        source: Source ID
        target: Target ID
        connection_type: Type (Feeder, Branch, Bus_Tie)
        label: Connection label

    Returns:
        Updated topology
    """
    topology["connections"].append(
        {
            "source": source,
            "target": target,
            "connection_type": connection_type,
            "label": label,
        }
    )
    return topology


def validate_topology(topology: dict) -> list[str]:
    """Validate topology references.

    Args:
        topology: Topology to validate

    Returns:
        List of validation errors
    """
    errors = []

    # Collect all IDs
    bus_ids = {b["id"] for b in topology.get("buses", [])}
    eq_ids = {e["id"] for e in topology.get("equipment", [])}
    all_ids = bus_ids | eq_ids

    # Check equipment parent_bus references
    for eq in topology.get("equipment", []):
        parent = eq.get("parent_bus")
        if parent and parent not in bus_ids:
            errors.append(f"Equipment '{eq['id']}' references unknown bus '{parent}'")

    # Check connection references
    for conn in topology.get("connections", []):
        if conn["source"] not in all_ids:
            errors.append(f"Connection source '{conn['source']}' not found")
        if conn["target"] not in all_ids:
            errors.append(f"Connection target '{conn['target']}' not found")

    return errors


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build or modify SLD topology"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="Input topology file to modify",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        required=True,
        help="Output topology file",
    )
    parser.add_argument(
        "--project",
        "-p",
        type=str,
        default="New Project",
        help="Project name (for new topology)",
    )
    parser.add_argument(
        "--validate",
        "-v",
        action="store_true",
        help="Validate topology and report errors",
    )

    args = parser.parse_args()

    # Load or create topology
    if args.input and args.input.exists():
        with open(args.input) as f:
            topology = yaml.safe_load(f)
    else:
        topology = create_empty_topology(args.project)

    # Validate if requested
    if args.validate:
        errors = validate_topology(topology)
        if errors:
            print("Validation errors:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            sys.exit(1)
        print("Topology is valid")

    # Save output
    with open(args.output, "w") as f:
        yaml.dump(topology, f, default_flow_style=False, sort_keys=False)
    print(f"Topology saved to: {args.output}")


if __name__ == "__main__":
    main()
