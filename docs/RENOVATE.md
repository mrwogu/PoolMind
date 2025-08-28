# Renovate Configuration for PoolMind

This document describes the Renovate configuration for the PoolMind project.

## Overview

Renovate is configured to automatically manage dependencies for this Python-based computer vision project. The configuration is optimized for the specific needs of a pool tracking system running on Raspberry Pi.

## Key Features

### 🔄 Automated Updates
- **Python packages**: Grouped by category (CV/ML, web framework, dev tools)
- **Docker images**: Python base images with digest pinning
- **GitHub Actions**: Auto-merge minor/patch updates
- **Pre-commit hooks**: Automatic updates with testing

### 🛡️ Security
- **Vulnerability alerts**: Immediate updates for critical security issues
- **OpenSSF Scorecard**: Security scoring for dependencies
- **Digest pinning**: Docker images pinned to specific digests

### 🎯 Project-Specific Rules

#### Computer Vision & ML Dependencies
- **Packages**: `numpy`, `opencv-python`, `imutils`, `scikit-learn`
- **Strategy**: Manual review required, 7-day minimum release age
- **Reason**: Hardware compatibility with Raspberry Pi camera systems

#### Web Framework
- **Packages**: `fastapi`, `uvicorn`, `starlette`, `pydantic`
- **Strategy**: Grouped updates, 3-day minimum release age
- **Reason**: API stability for real-time pool tracking

#### Raspberry Pi Specific
- **Special handling**: OpenCV and NumPy require hardware testing
- **Labels**: `raspberry-pi`, `hardware-specific`
- **Notes**: Added to PR descriptions for testing reminders

## Configuration Files

### Primary Configuration
- `renovate.json` - Main configuration file
- `.renovaterc.json` - Local development overrides
- `.github/renovate.json` - Organization-level backup

### Schedule
- **Regular updates**: Monday mornings (before 4 AM CET)
- **Security updates**: Immediate (any time)
- **Major versions**: First Monday of each month
- **Lock file maintenance**: Monday mornings

## Package Rules

### Auto-merge Enabled
✅ Development tools (pytest, black, flake8, mypy)
✅ Documentation tools (mkdocs)
✅ GitHub Actions (minor/patch)
✅ Pre-commit hooks
✅ Code quality tools

### Manual Review Required
⚠️ Computer vision packages (OpenCV, NumPy)
⚠️ Web framework (FastAPI, Uvicorn)
⚠️ Major version updates
⚠️ Security vulnerabilities

## Testing Strategy

### Automated Testing
- All updates trigger CI/CD pipeline
- Hardware-specific packages get additional validation
- Pre-commit hooks ensure code quality

### Hardware Testing
Computer vision updates should be tested on:
- Raspberry Pi 4B (primary target)
- Camera functionality
- ArUco marker detection
- Ball tracking performance

## Dashboard

The Renovate Dashboard provides:
- 📊 Overview of pending updates
- 🔍 Dependency insights
- ⚡ Quick actions for PRs
- 📈 Update statistics

Access the dashboard in GitHub Issues with title "🎱 PoolMind - Renovate Dashboard"

## Customization

### Adding New Package Rules
1. Edit `renovate.json`
2. Add to `packageRules` array
3. Test with `renovate-config-validator`
4. Commit changes

### Emergency Security Updates
Security vulnerabilities bypass all scheduling and are created immediately with:
- `security` and `critical` labels
- Highest priority (10)
- No auto-merge (manual review required)

## Troubleshooting

### Common Issues
1. **PR conflicts**: Renovate automatically rebases
2. **Failed checks**: Review CI logs for hardware-specific issues
3. **Missing updates**: Check dependency dashboard for blocked updates

### Debug Mode
Enable debug logging in `.renovaterc.json`:
```json
{
  "logLevel": "debug"
}
```

## Links
- [Renovate Documentation](https://docs.renovatebot.com/)
- [Configuration Options](https://docs.renovatebot.com/configuration-options/)
- [Dependency Dashboard](https://docs.renovatebot.com/key-concepts/dashboard/)
