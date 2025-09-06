# ACNE Changelog

All notable changes to ACNE will be documented in this file.

## [1.1.0-dev] - 2025-09-03

### Added
- Real Git integration and repository management
- Actual HuggingFace Space creation (replacing simulation)  
- Self-managing repository functionality
- Version management system with semantic versioning
- Enhanced conversation manager with Git commands
- Structured project directory with src/ and releases/

### Changed
- Improved deployment workflow from simulation to real deployment
- Enhanced error handling and user feedback
- Modular architecture with separate Git and HF managers

### Technical
- Added GitManager class for repository operations
- Added HuggingFaceDeployer for real Space creation
- Added VersionManager for release management
- Structured codebase with proper versioning

## [1.0.0] - 2025-09-03

### Added
- Initial ACNE implementation
- GitHub repository analysis
- Conversational deployment interface
- FastAPI backend with HTML frontend
- Deployment simulation
- Cost estimation
- Tech stack detection

### Features
- Repository analysis (auto-detects tech stacks)
- Cost estimation for deployments
- One-click deployment through conversation
- Real-time progress tracking
- Instant shareable URLs (simulated)

### Technical Details
- FastAPI 0.104.1
- GitHub API integration
- Docker deployment support
- Hugging Face Spaces compatible (port 7860)

---

**Versioning:** This project follows [Semantic Versioning](https://semver.org/).
**Format:** Based on [Keep a Changelog](https://keepachangelog.com/)
