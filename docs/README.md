# Documentation Source

This directory contains the source files for PoolMind documentation built with MkDocs.

## Structure

- **Source files**: All `.md` files in this directory
- **Configuration**: `../mkdocs.yml` in project root
- **Build output**: `../site/` (auto-generated, not in git)
- **Live site**: https://mrwogu.github.io/PoolMind

## Development

```bash
# Install dependencies
pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin

# Serve locally with auto-reload
mkdocs serve

# Build for production
mkdocs build --clean
```

## Files

- `index.md` - Homepage
- `QUICKSTART.md` - Getting started guide
- `CONFIGURATION.md` - Configuration reference
- `CALIBRATION.md` - Camera calibration guide
- `WEB.md` - Web interface documentation
- `ARCHITECTURE.md` - System architecture
- `FRONTEND.md` - Frontend development
- `MARKERS.md` - ArUco markers reference
- `RENOVATE.md` - Dependency management

## GitHub Pages

Documentation is automatically built and deployed by GitHub Actions on push to `main` branch.
The workflow builds the site and deploys it to GitHub Pages.
