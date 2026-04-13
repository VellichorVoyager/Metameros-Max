import unittest

from gradient_adk.server import invoke_entrypoint


def test_entrypoint(payload, context):
    return {"prompt": payload.get("prompt"), "trace": context.get("trace")}


class ServerTests(unittest.TestCase):
    def test_invoke_entrypoint_passes_payload_and_context(self):
        result = invoke_entrypoint(test_entrypoint, {"prompt": "hi"}, {"trace": "abc"})
        self.assertEqual(result, {"prompt": "hi", "trace": "abc"})


if __name__ == "__main__":
    unittest.main()
