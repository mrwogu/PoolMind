# Contributing Guidelines

This document provides guidelines for contributing to the project.

## Reporting Issues

When reporting issues, please include:

- Clear description of the issue
- Steps to reproduce the behavior
- Expected vs actual behavior
- Screenshots if applicable
- System information (OS, Python version, hardware)
- Log output if relevant

## Code Contributions

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes following the existing code style
4. Add tests for new functionality
5. Update documentation as needed
6. Test thoroughly on target hardware if possible
7. Submit a pull request with a clear description

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- Optional: Raspberry Pi 4 for hardware testing

### Local Development

```bash
# Clone the repository
git clone https://github.com/mrwogu/PoolMind.git
cd poolmind
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Coding Standards

- Follow PEP 8 style guide
- Use type hints for function signatures
- Write docstrings for public functions and classes
- Keep functions small and focused
- Use descriptive variable and function names
