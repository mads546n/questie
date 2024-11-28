import unittest
import main

from flask import template_rendered
from contextlib import contextmanager


class TestEvaluatePerformanceRoute(unittest.TestCase):
    def setUp(self):
        self.app = main.app.test_client()
        self.app.testing = True

    @contextmanager
    def captured_templates(self):
        recorded = []

        def record(sender, template, context, **extra):
            recorded.append((template, context))

        template_rendered.connect(record, main.app)
        try:
            yield recorded
        finally:
            template_rendered.disconnect(record, main.app)

    def test_evaluate_performance_route(self):
        with self.captured_templates() as templates:
            response = self.app.get('/evaluate')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'evaluate.html')

            # Ensure performance_data and graph_urls are in context
            self.assertIn('performance_data', context)
            self.assertIn('graph_urls', context)


if __name__ == '__main__':
    unittest.main()
