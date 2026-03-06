# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-03-06

### Added

- `Config.from_dict()` factory method for constructing configs from dictionaries
- `__version__` attribute exposed via `importlib.metadata`
- Coverage threshold (90%) enforced in test suite
- Thread safety guarantees documented on `Config` class

### Fixed

- Empty config files now raise a clear `CofferError("Config file is empty")` instead of a confusing `NoneType` message

## [0.1.0] - 2026-03-06

### Added

- Initial release
- `Config` class with dot-notation access, type coercion, and `Mapping` protocol
- `Config.from_file()` for JSON and YAML files
- `CofferError` exception class
- CI pipeline with ruff, mypy, and pytest across Python 3.10-3.13
- PyPI publish workflow via GitHub Releases
