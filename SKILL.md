---
name: electrical-distribution-skill
description: |
  Generates single-line diagrams (SLDs) from load lists using PlantUML.

  Produces:
  1. Machine-readable SLD topology (YAML)
  2. PlantUML source (text, git-diffable)
  3. Rendered diagrams (PNG/SVG)
  4. Shareable PlantUML URLs
  5. Optional: pandapower analysis (short-circuit, voltage drop)

  NOTE: Output is for engineering review, not contractor submission.
  CAD packaging can be outsourced to drafters using the topology as reference.

  Inputs: load-list-skill output
  Outputs: SLD topology YAML, PlantUML source, PNG/SVG diagrams
mcp_server: plantuml-sld-mcp-server
version: 0.1.0
---

# Electrical Distribution Skill

## Overview

This skill generates electrical single-line diagrams (SLDs) from load list data.
It follows the **puran-water philosophy** of machine-readable YAML as the source
of truth, with PlantUML providing git-diffable visualization.

### Alignment with Puran Water Philosophy

| Principle | Implementation |
|-----------|----------------|
| **Open-Source Stack** | PlantUML (no AutoCAD license), pandapower (no ETAP/SKM) |
| **Machine-Readable Formats** | YAML topology → PlantUML text (git-diffable) |
| **Git-Native Workflows** | Text-based SLD source, version-controlled diagrams |
| **Physics-Based Calculations** | pandapower IEC 60909 short-circuit (optional) |

## Prerequisites

- **load-list-skill** output (electrical/load-list.yaml)
- **plantuml-sld-mcp-server** configured in Claude Code

## Workflow

### 1. Bootstrap from Load List

Start by importing equipment from load-list-skill output:

```yaml
# Load list provides:
# - Equipment tags and ratings
# - MCC panel assignments
# - Feeder types (DOL, VFD, Soft-Starter)
# - Protection sizing
```

Use the `sld_bootstrap_from_loadlist` tool with a distribution template:

- `single_utility_radial`: Simple utility → transformer → MSB → MCCs
- `utility_plus_generator`: Adds standby generator with ATS
- `dual_utility_redundant`: Split bus with tie breaker for redundancy

### 2. Review and Customize Topology

The bootstrap creates a draft topology. Review and customize:

- Add missing equipment (UPS, capacitor banks, etc.)
- Adjust bus names and descriptions
- Add cable sizing and lengths
- Configure protection ratings

### 3. Generate PlantUML and Render

Use MCP tools to generate diagrams:

1. `sld_validate_topology` - Validate the YAML
2. `sld_get_plantuml_source` - Generate PlantUML source
3. `sld_generate_diagram` - Render to PNG/SVG
4. `sld_encode_plantuml` - Get shareable URL

### 4. View Modes

Two view modes are supported:

- **System View** (collapsed): Shows buses with aggregated loads
  - Best for: Overview diagrams, utility coordination
  - Generated from Tier 1 load lists

- **Detailed View** (expanded): Shows individual feeders per bus
  - Best for: Engineering review, panel layouts
  - Requires Tier 2/3 load list data

## MCP Tools

| Tool | Purpose |
|------|---------|
| `sld_validate_topology` | Validate SLD topology YAML |
| `sld_get_plantuml_source` | Generate PlantUML source |
| `sld_get_plantuml_source_per_bus` | Generate PlantUML for single bus/MCC |
| `sld_generate_diagram` | Render to PNG/SVG |
| `sld_encode_plantuml` | Generate shareable URLs |
| `sld_check_plantuml` | Check PlantUML availability |
| `sld_list_symbols` | List available electrical symbols |
| `sld_bootstrap_from_loadlist` | Import from load-list output |

## Schema

The SLD topology schema is defined in `schemas/sld-topology.schema.yaml`.

Key components:

### Buses (SLDBus)
- Main Switchboards, MCCs, Distribution Panels
- Voltage level, current rating, SCCR

### Equipment (SLDEquipment)
- Sources: Utility, Generator, UPS, PV
- Transformers: Main, distribution
- Protective devices: ACB, MCCB, Fuses
- Starters: DOL, VFD, Soft Starter
- Loads: Motors, Heaters, Vendor Packages

### Connections (SLDConnection)
- Feeders, Branch circuits
- Bus ties, couplers
- State: Open/Closed for switchable devices

## Output Examples

### System View (Collapsed)
```
Utility 11kV
    │
    ▼
XFMR-01 1000kVA 11kV/400V
    │
    ▼
┌─────────────────────────────┐
│ MSB-01 400V 2500A           │
│  ├─ MCC-100 (320 kW, 12 fdrs)│
│  ├─ MCC-200 (580 kW, 18 fdrs)│
│  └─ MCC-300 (210 kW, 8 fdrs) │
└─────────────────────────────┘
```

### Detailed View (Expanded)
```
┌─ MCC-200 Biological ─────────────┐
│ 400V 630A                        │
│                                  │
│  200-B-01A Blower #1 90kW VFD    │
│  200-B-02A Blower #2 90kW VFD    │
│  200-MX-01 Mixer 7.5kW DOL       │
│  200-P-01A RAS Pump 15kW VFD     │
│  ...                             │
└──────────────────────────────────┘
```

## Limitations

- **Not contractor-submission ready**: Output is for engineering review
- **No CAD output**: Use topology as reference for CAD drafters
- **Simplified protection**: Basic protection representation only
- **No coordination studies**: Use dedicated software (ETAP, SKM)

## Directory Structure

```
electrical-distribution-skill/
├── SKILL.md                      # This file
├── schemas/
│   └── sld-topology.schema.yaml  # SLD topology schema
├── scripts/
│   ├── import_load_list.py       # Load list parser helper
│   ├── build_sld_topology.py     # Topology builder helper
│   └── validate_sld.py           # Topology validation script
├── templates/
│   └── sld-report.qmd            # Design report template
└── references/
    └── sld-conventions.md        # SLD symbology reference
```

## Related Skills

- **load-list-skill**: Provides equipment and load data (upstream)
- **instrument-io-skill**: Provides IO counts for control architecture
- **plantuml-csa-mcp-server**: Control system architecture diagrams

## Versioning

- Schema version: 1.0
- Skill version: 0.1.0

## License

MIT License - Puran Water
