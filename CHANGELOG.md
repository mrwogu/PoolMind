# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release preparation
- Complete documentation suite
- CI/CD pipeline setup
- Docker containerization
- DevContainer configuration
- 🤖 **Renovate Integration**: Comprehensive automated dependency management
  - Smart grouping of computer vision, web framework, and development dependencies
  - Hardware-specific validation for Raspberry Pi compatibility
  - Security vulnerability monitoring with immediate updates
  - Scheduled updates (Monday mornings) with auto-merge for safe updates
  - Custom configuration for pool project needs
  - GitHub Actions workflow for configuration validation
  - Detailed documentation in `docs/RENOVATE.md`

## [1.0.0] - 2025-08-28

### Added
- 🎥 Real-time ball detection and tracking using OpenCV and HoughCircles
- 🎯 ArUco marker-based camera calibration with EMA smoothing
- 🎱 Advanced HSV-based color classification (cue, solid, stripe balls)
- 🎮 Complete 8-ball rules engine with automatic game state management
- 📹 Motion-triggered instant replay recording system
- 🌐 FastAPI-powered web dashboard with live MJPEG streaming
- 📊 Real-time game statistics and ball tracking visualization
- 🔧 Modular architecture for easy customization and extension
- 🚀 Production-ready systemd service integration
- 📱 Responsive web interface with real-time updates
- 🎯 Automatic pocket detection and ball potting events
- 📈 Performance monitoring and FPS display
- 🔄 Graceful hardware degradation for development without camera
- 🛠️ Comprehensive configuration system via YAML
- 📚 Complete documentation with setup guides
- 🎪 ArUco marker generation tools with PDF export
- 🐳 Docker containerization with multi-stage builds
- 🔧 Automated installation and setup scripts
- 🧪 Development tools and testing framework
- 🌈 Visual overlays with ball trails and game information

### Technical Features
- Threaded camera capture for optimal performance
- Centroid-based object tracking with ID persistence
- Homography transformation for bird's-eye table view
- EMA filtering for stable ball position tracking
- Motion detection for replay triggering
- RESTful API for external integrations
- WebSocket support for real-time updates
- Configurable detection parameters
- Multi-platform support (ARM64/x86_64)
- Hardware abstraction layer

### Documentation
- Complete installation guide for Raspberry Pi
- Hardware setup and calibration instructions
- Configuration reference with parameter tuning
- Architecture overview and component documentation
- Troubleshooting guide with common solutions
- Contributing guidelines for developers
- Security policy and best practices
- API documentation with examples

### Infrastructure
- GitHub Actions CI/CD pipeline
- Automated testing with pytest
- Code quality tools (black, flake8, mypy)
- Pre-commit hooks for development
- Docker multi-stage builds
- VS Code DevContainer configuration
- Security scanning with bandit and trivy
- Documentation generation with MkDocs

[Unreleased]: https://github.com/mrwogu/PoolMind/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/mrwogu/PoolMind/releases/tag/v1.0.0
