import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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


def sample_entry(payload, context):
    return payload


if __name__ == "__main__":
    unittest.main()
