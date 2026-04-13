import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gradient_adk.config import (
    ENV_API_KEY,
    get_api_key,
    load_config,
    save_config,
    validate_required_env,
)


class ConfigTests(unittest.TestCase):
    def _isolated_config(self, tmp_dir: str):
        """Return a context manager that redirects config to a temp directory."""
        config_dir = Path(tmp_dir) / ".gradient"
        config_file = config_dir / "config.json"
        import gradient_adk.config as cfg_module

        return patch.multiple(
            cfg_module,
            CONFIG_DIR=config_dir,
            CONFIG_FILE=config_file,
        )

    def test_load_config_returns_empty_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp):
                self.assertEqual(load_config(), {})

    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp):
                data = {"api_key": "test-key", "agent_id": "ag-123"}
                save_config(data)
                self.assertEqual(load_config(), data)

    def test_get_api_key_from_env(self):
        with patch.dict(os.environ, {ENV_API_KEY: "env-key"}):
            self.assertEqual(get_api_key(), "env-key")

    def test_get_api_key_from_config(self):
        with patch.dict(os.environ, {}, clear=True):
            # Ensure the env var is absent
            os.environ.pop(ENV_API_KEY, None)
            self.assertEqual(get_api_key({"api_key": "cfg-key"}), "cfg-key")

    def test_get_api_key_env_overrides_config(self):
        with patch.dict(os.environ, {ENV_API_KEY: "env-wins"}):
            self.assertEqual(get_api_key({"api_key": "cfg-key"}), "env-wins")

    def test_get_api_key_returns_none_when_absent(self):
        os.environ.pop(ENV_API_KEY, None)
        self.assertIsNone(get_api_key({}))

    def test_load_config_handles_corrupt_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp):
                import gradient_adk.config as cfg_module

                cfg_module.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
                cfg_module.CONFIG_FILE.write_text("not-json", encoding="utf-8")
                self.assertEqual(load_config(), {})


class ValidateRequiredEnvTests(unittest.TestCase):
    def test_passes_when_all_vars_are_set(self):
        with patch.dict(os.environ, {"MY_VAR": "value"}):
            validate_required_env("MY_VAR")  # should not raise

    def test_raises_system_exit_when_var_missing(self):
        env = os.environ.copy()
        env.pop("MISSING_VAR_XYZ", None)
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(SystemExit) as cm:
                validate_required_env("MISSING_VAR_XYZ")
            self.assertEqual(cm.exception.code, 1)

    def test_raises_system_exit_listing_all_missing(self):
        env = os.environ.copy()
        env.pop("MISSING_A", None)
        env.pop("MISSING_B", None)
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(SystemExit):
                validate_required_env("MISSING_A", "MISSING_B")


if __name__ == "__main__":
    unittest.main()
