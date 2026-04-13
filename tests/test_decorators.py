import unittest

from gradient_adk.decorators import entrypoint, trace_llm, trace_retriever, trace_tool


class DecoratorTests(unittest.TestCase):
    def test_entrypoint_marks_function(self):
        @entrypoint
        def fn(payload, context):
            return payload

        self.assertTrue(getattr(fn, "__gradient_entrypoint__", False))

    def test_trace_decorators_add_events(self):
        @trace_llm
        def llm(payload, context):
            return "ok"

        @trace_tool
        def tool(payload, context):
            return "ok"

        @trace_retriever
        def retriever(payload, context):
            return "ok"

        context = {}
        llm({}, context)
        tool({}, context)
        retriever({}, context)

        self.assertEqual(
            [event["type"] for event in context["trace_events"]],
            ["llm", "tool", "retriever"],
        )


if __name__ == "__main__":
    unittest.main()
