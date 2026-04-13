import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gradient_adk.cli import _load_callable, main


class CliTests(unittest.TestCase):
    def test_init_creates_agent_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc = main(["agent", "init", tmp])
            self.assertEqual(rc, 0)
            self.assertTrue((Path(tmp) / "agent.py").exists())

    def test_load_callable_requires_module_function_format(self):
        with self.assertRaises(ValueError):
            _load_callable("invalid")

    def test_run_calls_server(self):
        with patch("gradient_adk.cli.run_server") as run_server:
            rc = main(["agent", "run", "--module", "tests.test_cli:sample_entry"])
            self.assertEqual(rc, 0)
            self.assertTrue(run_server.called)

    # ------------------------------------------------------------------
    # configure
    # ------------------------------------------------------------------

    def test_configure_saves_api_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp):
                rc = main(["agent", "configure", "--api-key", "mykey123"])
                self.assertEqual(rc, 0)
                import gradient_adk.config as cfg

                saved = json.loads(cfg.CONFIG_FILE.read_text())
                self.assertEqual(saved["api_key"], "mykey123")

    def test_configure_saves_agent_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp):
                rc = main(["agent", "configure", "--agent-id", "ag-42"])
                self.assertEqual(rc, 0)
                import gradient_adk.config as cfg

                saved = json.loads(cfg.CONFIG_FILE.read_text())
                self.assertEqual(saved["agent_id"], "ag-42")

    def test_configure_no_args_prints_current_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp):
                import gradient_adk.config as cfg

                cfg.save_config({"api_key": "existingkey", "agent_id": "ag-1"})
                # Should not raise; rc should be 0
                rc = main(["agent", "configure"])
                self.assertEqual(rc, 0)

    # ------------------------------------------------------------------
    # deploy
    # ------------------------------------------------------------------

    def test_deploy_fails_without_api_key(self):
        os.environ.pop("GRADIENT_API_KEY", None)
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp):
                rc = main(["agent", "deploy", "--module", "tests.test_cli:sample_entry"])
                self.assertEqual(rc, 1)

    def test_deploy_calls_client(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp), patch.dict(
                os.environ, {"GRADIENT_API_KEY": "k"}
            ):
                mock_client = MagicMock()
                mock_client.deploy_agent.return_value = {
                    "agent_id": "ag-99",
                    "status": "deploying",
                }
                with patch("gradient_adk.cli.GradientClient", return_value=mock_client):
                    rc = main(
                        [
                            "agent",
                            "deploy",
                            "--module",
                            "tests.test_cli:sample_entry",
                            "--name",
                            "test-agent",
                        ]
                    )
                self.assertEqual(rc, 0)
                mock_client.deploy_agent.assert_called_once_with(
                    name="test-agent",
                    module="tests.test_cli:sample_entry",
                    region="nyc3",
                )

    def test_deploy_invalid_module_returns_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp), patch.dict(
                os.environ, {"GRADIENT_API_KEY": "k"}
            ):
                rc = main(["agent", "deploy", "--module", "no_such_module:fn"])
                self.assertEqual(rc, 1)

    # ------------------------------------------------------------------
    # traces
    # ------------------------------------------------------------------

    def test_traces_fails_without_api_key(self):
        os.environ.pop("GRADIENT_API_KEY", None)
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp):
                rc = main(["agent", "traces", "--agent-id", "ag-1"])
                self.assertEqual(rc, 1)

    def test_traces_fails_without_agent_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp), patch.dict(
                os.environ, {"GRADIENT_API_KEY": "k"}
            ):
                rc = main(["agent", "traces"])
                self.assertEqual(rc, 1)

    def test_traces_calls_client(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp), patch.dict(
                os.environ, {"GRADIENT_API_KEY": "k"}
            ):
                mock_client = MagicMock()
                mock_client.get_traces.return_value = [
                    {"type": "llm", "name": "fn"}
                ]
                with patch("gradient_adk.cli.GradientClient", return_value=mock_client):
                    rc = main(["agent", "traces", "--agent-id", "ag-1", "--limit", "5"])
                self.assertEqual(rc, 0)
                mock_client.get_traces.assert_called_once_with("ag-1", limit=5)

    # ------------------------------------------------------------------
    # logs
    # ------------------------------------------------------------------

    def test_logs_fails_without_api_key(self):
        os.environ.pop("GRADIENT_API_KEY", None)
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp):
                rc = main(["agent", "logs", "--agent-id", "ag-1"])
                self.assertEqual(rc, 1)

    def test_logs_fails_without_agent_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp), patch.dict(
                os.environ, {"GRADIENT_API_KEY": "k"}
            ):
                rc = main(["agent", "logs"])
                self.assertEqual(rc, 1)

    def test_logs_calls_client(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp), patch.dict(
                os.environ, {"GRADIENT_API_KEY": "k"}
            ):
                mock_client = MagicMock()
                mock_client.get_logs.return_value = [
                    {"timestamp": "2024-01-01T00:00:00Z", "message": "started"}
                ]
                with patch("gradient_adk.cli.GradientClient", return_value=mock_client):
                    rc = main(["agent", "logs", "--agent-id", "ag-1", "--limit", "50"])
                self.assertEqual(rc, 0)
                mock_client.get_logs.assert_called_once_with("ag-1", limit=50)

    def test_logs_uses_agent_id_from_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self._isolated_config(tmp), patch.dict(
                os.environ, {"GRADIENT_API_KEY": "k"}
            ):
                import gradient_adk.config as cfg

                cfg.save_config({"agent_id": "ag-from-cfg"})
                mock_client = MagicMock()
                mock_client.get_logs.return_value = []
                with patch("gradient_adk.cli.GradientClient", return_value=mock_client):
                    rc = main(["agent", "logs"])
                self.assertEqual(rc, 0)
                mock_client.get_logs.assert_called_once_with("ag-from-cfg", limit=100)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _isolated_config(tmp_dir: str):
        config_dir = Path(tmp_dir) / ".gradient"
        config_file = config_dir / "config.json"
        import gradient_adk.config as cfg_module

        return patch.multiple(
            cfg_module,
            CONFIG_DIR=config_dir,
            CONFIG_FILE=config_file,
        )


def sample_entry(payload, context):
    return payload


if __name__ == "__main__":
    unittest.main()

