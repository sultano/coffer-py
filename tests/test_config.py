from __future__ import annotations

import pytest

from coffer import CofferError, Config


# --- __init__ and to_dict ---


class TestInitAndToDict:
    def test_stores_data(self):
        config = Config({"key": "value"})
        assert config.to_dict() == {"key": "value"}

    def test_to_dict_returns_deep_copy(self):
        original = {"nested": {"a": 1}}
        config = Config(original)
        copy = config.to_dict()
        copy["nested"]["a"] = 999
        assert config.to_dict()["nested"]["a"] == 1

    def test_empty_dict(self):
        config = Config({})
        assert config.to_dict() == {}

    def test_constructor_copies_input(self):
        original = {"key": "value"}
        config = Config(original)
        original["key"] = "changed"
        assert config.get("key") == "value"


# --- from_file ---


class TestFromFile:
    def test_reads_json(self, tmp_json_config):
        path = tmp_json_config({"host": "localhost"})
        config = Config.from_file(path)
        assert config.get("host") == "localhost"

    def test_reads_yaml(self, tmp_yaml_config):
        path = tmp_yaml_config({"host": "localhost"})
        config = Config.from_file(path)
        assert config.get("host") == "localhost"

    def test_reads_yml_extension(self, tmp_yaml_config):
        path = tmp_yaml_config({"host": "localhost"}, name="config.yml")
        config = Config.from_file(path)
        assert config.get("host") == "localhost"

    def test_missing_file(self, tmp_path):
        with pytest.raises(CofferError, match="Cannot read file"):
            Config.from_file(tmp_path / "nonexistent.json")

    def test_invalid_json(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text("{not valid json")
        with pytest.raises(CofferError, match="Failed to parse"):
            Config.from_file(p)

    def test_invalid_yaml(self, tmp_path):
        p = tmp_path / "bad.yaml"
        p.write_text(":\n  :\n    - ][")
        with pytest.raises(CofferError, match="Failed to parse"):
            Config.from_file(p)

    def test_unknown_extension(self, tmp_path):
        p = tmp_path / "config.toml"
        p.write_text("")
        with pytest.raises(CofferError, match="Unsupported file extension"):
            Config.from_file(p)

    def test_non_dict_root(self, tmp_json_config):
        path = tmp_json_config([1, 2, 3], name="list.json")
        with pytest.raises(CofferError, match="mapping at the root"):
            Config.from_file(path)


# --- get: basic access ---


class TestGetBasic:
    def test_top_level_key(self):
        config = Config({"host": "localhost"})
        assert config.get("host") == "localhost"

    def test_dot_notation_nested(self):
        config = Config({"database": {"host": "localhost"}})
        assert config.get("database.host") == "localhost"

    def test_deeply_nested(self):
        config = Config({"a": {"b": {"c": {"d": 42}}}})
        assert config.get("a.b.c.d") == 42

    def test_missing_key_raises_keyerror(self):
        config = Config({"a": 1})
        with pytest.raises(KeyError, match="missing.key"):
            config.get("missing.key")

    def test_missing_key_with_default(self):
        config = Config({})
        assert config.get("missing", default="fallback") == "fallback"

    def test_default_none(self):
        config = Config({})
        assert config.get("missing", default=None) is None

    def test_missing_intermediate_with_default(self):
        config = Config({"a": {"b": 1}})
        assert config.get("a.x.y", default="fallback") == "fallback"

    def test_returns_raw_types(self):
        config = Config({"i": 42, "l": [1, 2], "d": {"a": 1}})
        assert config.get("i") == 42
        assert config.get("l") == [1, 2]

    def test_nested_dict_returns_config(self):
        config = Config({"d": {"a": 1}})
        sub = config.get("d")
        assert isinstance(sub, Config)
        assert sub.get("a") == 1


# --- get: type coercion ---


class TestGetTypeCoercion:
    def test_int_from_string(self):
        config = Config({"port": "5432"})
        assert config.get("port", type=int) == 5432

    def test_int_passthrough(self):
        config = Config({"port": 5432})
        assert config.get("port", type=int) == 5432

    def test_float_from_string(self):
        config = Config({"rate": "0.5"})
        assert config.get("rate", type=float) == 0.5

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
        ],
    )
    def test_bool_from_string(self, raw, expected):
        config = Config({"flag": raw})
        assert config.get("flag", type=bool) is expected

    def test_bool_passthrough(self):
        config = Config({"flag": True})
        assert config.get("flag", type=bool) is True

    def test_bool_from_int_one(self):
        config = Config({"flag": 1})
        assert config.get("flag", type=bool) is True

    def test_bool_from_int_zero(self):
        config = Config({"flag": 0})
        assert config.get("flag", type=bool) is False

    def test_bool_from_int_other_raises(self):
        config = Config({"flag": 2})
        with pytest.raises(TypeError, match="Cannot coerce"):
            config.get("flag", type=bool)

    def test_str_from_int(self):
        config = Config({"port": 5432})
        assert config.get("port", type=str) == "5432"

    def test_list_from_csv(self):
        config = Config({"tags": "a, b, c"})
        assert config.get("tags", type=list) == ["a", "b", "c"]

    def test_list_passthrough(self):
        config = Config({"tags": [1, 2, 3]})
        assert config.get("tags", type=list) == [1, 2, 3]

    def test_int_from_non_numeric_raises_typeerror(self):
        config = Config({"port": "abc"})
        with pytest.raises(TypeError, match="Cannot coerce"):
            config.get("port", type=int)

    def test_type_applied_to_default(self):
        config = Config({})
        assert config.get("port", default="8080", type=int) == 8080


# --- __getitem__ ---


class TestGetItem:
    def test_scalar_value(self):
        config = Config({"host": "localhost"})
        assert config["host"] == "localhost"

    def test_nested_dict_returns_config(self):
        config = Config({"db": {"host": "localhost"}})
        sub = config["db"]
        assert isinstance(sub, Config)
        assert sub["host"] == "localhost"

    def test_missing_key_raises_keyerror(self):
        config = Config({})
        with pytest.raises(KeyError):
            config["missing"]

    def test_chained_access(self):
        config = Config({"a": {"b": {"c": 1}}})
        assert config["a"]["b"]["c"] == 1

    def test_dot_notation(self):
        config = Config({"a": {"b": 1}})
        assert config["a.b"] == 1

    def test_list_value(self):
        config = Config({"items": [1, 2, 3]})
        assert config["items"] == [1, 2, 3]


# --- __contains__ ---


class TestContains:
    def test_top_level_present(self):
        config = Config({"host": "localhost"})
        assert "host" in config

    def test_top_level_absent(self):
        config = Config({"host": "localhost"})
        assert "missing" not in config

    def test_dot_notation_present(self):
        config = Config({"database": {"host": "localhost"}})
        assert "database.host" in config

    def test_dot_notation_absent(self):
        config = Config({"database": {"host": "localhost"}})
        assert "database.missing" not in config


# --- __iter__ and __len__ ---


class TestIterAndLen:
    def test_iter_top_level_keys(self):
        config = Config({"a": 1, "b": 2, "c": 3})
        assert set(config) == {"a", "b", "c"}

    def test_len(self):
        config = Config({"a": 1, "b": 2})
        assert len(config) == 2


# --- __eq__ ---


class TestEq:
    def test_equal(self):
        assert Config({"a": 1}) == Config({"a": 1})

    def test_not_equal(self):
        assert Config({"a": 1}) != Config({"a": 2})

    def test_not_equal_to_non_config(self):
        assert Config({"a": 1}) != {"a": 1}


# --- __repr__ ---


class TestRepr:
    def test_contains_class_name(self):
        config = Config({"a": 1})
        r = repr(config)
        assert "Config" in r
        assert "'a'" in r
