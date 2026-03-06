from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml


@pytest.fixture()
def tmp_json_config(tmp_path: Path):
    def _make(data: Any, name: str = "config.json") -> Path:
        p = tmp_path / name
        p.write_text(json.dumps(data))
        return p

    return _make


@pytest.fixture()
def tmp_yaml_config(tmp_path: Path):
    def _make(data: Any, name: str = "config.yaml") -> Path:
        p = tmp_path / name
        p.write_text(yaml.dump(data))
        return p

    return _make
