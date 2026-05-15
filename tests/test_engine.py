import unittest
from main import evaluate


class TestAssessmentEngine(unittest.TestCase):

    def test_elite_score(self):
        self.assertEqual(
            evaluate(10, 10),
            "MERCOR ELITE"
        )

    def test_high_performer(self):
        self.assertEqual(
            evaluate(8, 10),
            "HIGH PERFORMER"
        )

    def test_strong(self):
        self.assertEqual(
            evaluate(6, 10),
            "STRONG"
        )

    def test_developing(self):
        self.assertEqual(
            evaluate(4, 10),
            "DEVELOPING"
        )

    def test_needs_improvement(self):
        self.assertEqual(
            evaluate(2, 10),
            "NEEDS IMPROVEMENT"
        )


if __name__ == "__main__":
    unittest.main()