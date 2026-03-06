# coffer-config

Typed config reader for resolved [Coffer](https://github.com/sul/coffer) config files.

Coffer is a Go CLI that merges YAML configs, resolves secrets from GCP Secret Manager, and outputs a resolved config file. This library reads those pre-resolved files and provides ergonomic, type-safe access. No secret resolution, no GCP dependency.

## Install

```bash
pip install coffer-config
```

## Usage

```python
from coffer import Config

# Load from a resolved config file (JSON or YAML)
config = Config.from_file("config.json")

# Dot-notation access
host = config.get("database.host")
port = config.get("database.port", type=int)
debug = config.get("debug", default=False, type=bool)

# Dict-style access (nested dicts become Config objects)
db = config["database"]
db["host"]  # "localhost"

# Membership and iteration
"database.host" in config  # True
list(config)               # top-level keys

# Raw dict
config.to_dict()
```

## Development

```bash
pip install -e ".[dev]"
pre-commit install
```

## Limitations

- **Dot-separated keys**: Keys containing literal dots (e.g. `{"a.b": 1}`) are not accessible via dot-notation. Use `config.to_dict()` to access them directly.

## Type coercion

The `type=` parameter on `get()` coerces values:

| `type=` | Behavior |
|---------|----------|
| `int` | `int(value)` |
| `float` | `float(value)` |
| `bool` | `"true"/"1"/"yes"` -> True, `"false"/"0"/"no"` -> False (case-insensitive) |
| `str` | `str(value)` |
| `list` | If string, splits on `,` and strips whitespace. Lists pass through. |
