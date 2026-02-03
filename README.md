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

## Related

- [plantuml-sld-mcp-server](https://github.com/puran-water/plantuml-sld-mcp-server) - MCP server
- [load-list-skill](https://github.com/puran-water/load-list-skill) - Upstream data

## License

MIT License - Puran Water
