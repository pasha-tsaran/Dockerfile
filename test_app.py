"""Проверка арифметики и валидации Flask API: python -m unittest -v."""

import unittest

from app import app


class CalculatorTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_operations(self):
        for operation, a, b, expected in (
            ("add", 12, 5, 17), ("subtract", 12, 5, 7),
            ("subtract", -2, 5, -7), ("add", 1.25, 2.5, 3.75), ("add", 0, 0, 0),
        ):
            with self.subTest(operation=operation, a=a, b=b):
                response = self.client.post("/api/calculate", json={
                    "operation": operation, "a": a, "b": b})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json["result"], expected)

    def test_invalid_input(self):
        for data in (None, [], {}, {"a": 1, "b": 2, "operation": "multiply"},
                     {"a": True, "b": 2, "operation": "add"},
                     {"a": "1", "b": 2, "operation": "add"},
                     {"a": 1e308, "b": 1e308, "operation": "add"},
                     {"a": float("inf"), "b": 1, "operation": "add"},
                     {"a": 10**400, "b": 1, "operation": "add"}):
            with self.subTest(data=data):
                response = self.client.post("/api/calculate", json=data)
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.json)

    def test_malformed_json(self):
        response = self.client.post("/api/calculate", data="{", content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_health_and_errors(self):
        self.assertEqual(self.client.get("/health").json["status"], "ok")
        self.assertEqual(self.client.get("/api/health").status_code, 200)
        self.assertEqual(self.client.get("/missing").status_code, 404)
        self.assertEqual(self.client.get("/api/calculate").status_code, 405)
        self.assertEqual(self.client.post("/api/calculate", data="x" * 5000,
                                         content_type="application/json").status_code, 413)


if __name__ == "__main__":
    unittest.main()
