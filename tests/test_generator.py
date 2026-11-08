import json
import unittest
from pathlib import Path
from generator import generate, load_spec

class GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = load_spec(Path(__file__).resolve().parents[1] / 'examples/petstore.json')
        cls.cases = generate(cls.spec)

    def test_generates_success_cases(self):
        self.assertEqual(sum(c['type'] == 'documented_success' for c in self.cases), 3)

    def test_required_path_parameter(self):
        self.assertTrue(any(c.get('parameter') == 'petId' for c in self.cases))

    def test_authentication_case(self):
        self.assertTrue(any(c['type'] == 'missing_authentication' for c in self.cases))

    def test_expected_status_from_spec(self):
        self.assertEqual(next(c['expected_status'] for c in self.cases if c['id'] == 'createPet:success'), ['201'])

    def test_rejects_invalid_openapi(self):
        with self.assertRaises(ValueError):
            generate({'swagger': '2.0', 'paths': {}})

    def test_deterministic(self):
        self.assertEqual(self.cases, generate(self.spec))

if __name__ == '__main__':
    unittest.main()
