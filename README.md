# Electrical Distribution Skill

Claude Code skill for generating electrical single-line diagrams (SLDs) from load lists.

## Quick Start

This skill uses the [plantuml-sld-mcp-server](https://github.com/puran-water/plantuml-sld-mcp-server) to generate SLD diagrams from YAML topology definitions.

### Prerequisites

1. Configure `plantuml-sld-mcp-server` in Claude Code
2. Have a load list from `load-list-skill`

### Basic Workflow

1. Bootstrap topology from load list using `sld_bootstrap_from_loadlist`
2. Validate with `sld_validate_topology`
3. Generate diagram with `sld_generate_diagram`

## Documentation

See [SKILL.md](SKILL.md) for complete documentation including:

- Workflow details
- MCP tool reference
- Schema documentation
- Output examples
- Limitations

## Files

| Path | Description |
|------|-------------|
| `SKILL.md` | Full skill documentation |
| `schemas/sld-topology.schema.yaml` | SLD topology schema |
| `scripts/` | Helper scripts for topology operations |
| `templates/sld-report.qmd` | Quarto report template |
| `references/sld-conventions.md` | SLD symbology reference |

## Workflow Integration

This skill is part of the puran-water electrical engineering workflow:

```
┌─────────────────────────┐     ┌──────────────────────────┐     ┌─────────────────────┐
│  equipment-list-skill   │ ──► │    load-list-skill       │ ──► │ electrical-         │
│  (equipment + power_kw) │     │    (FLC, protection,     │     │ distribution-skill  │
└─────────────────────────┘     │     MCC schedules)       │     │ (this skill)        │
                                └──────────────────────────┘     └─────────────────────┘
                                                                            │
                                                                            ▼
                                                                 ┌─────────────────────┐
                                                                 │ plantuml-sld-mcp    │
                                                                 │ (MCP server)        │
                                                                 └─────────────────────┘
                                                                            │
                                                                            ▼
                                                                 ┌─────────────────────┐
                                                                 │ SLD Topology YAML   │
                                                                 │ PlantUML PNG/SVG    │
                                                                 │ Shareable URLs      │
                                                                 └─────────────────────┘
```

## Related

### MCP Server
- [plantuml-sld-mcp-server](https://github.com/puran-water/plantuml-sld-mcp-server) - MCP server that renders SLDs

### Upstream Skills (Data Sources)
- [load-list-skill](https://github.com/puran-water/load-list-skill) - Electrical load lists with MCC schedules
- [equipment-list-skill](https://github.com/puran-water/equipment-list-skill) - Equipment lists with power ratings

### Similar Pattern (Control Systems)
- [csa-diagram-skill](https://github.com/puran-water/csa-diagram-skill) - Control System Architecture diagrams
- [plantuml-csa-mcp-server](https://github.com/puran-water/plantuml-csa-mcp-server) - CSA MCP server

## License

MIT License - Puran Water
