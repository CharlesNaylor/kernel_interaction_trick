"""
Tests for DataGenerator
"""
import logging
import unittest

from src.generate_data import DataGenerator

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestDataGenerator(unittest.TestCase):
    """tests for DataGenerator"""

    def setUp(self):
        self.json_path = "test.json"

    def test_io(self):
        dg = DataGenerator(name="test")
        expected_log = f"Wrote data generator configuration to {self.json_path}"
        with self.assertLogs("src.generate_data") as j_logs:
            dg.to_json(self.json_path)
        self.assertEqual(j_logs.output, ["INFO:src.generate_data:" + expected_log])

        dg2 = DataGenerator.from_json(self.json_path)
        self.assertEqual(dg, dg2)

    def test_simulate(self):
        dg = DataGenerator(name="test")
        expected_log = f"Generated exogs and endo using data generator {dg.name}, version {dg.version}"
        with self.assertLogs("src.generate_data") as sim_logs:
            exogs, endos = dg.simulate()
        self.assertEqual(sim_logs.output, ["INFO:src.generate_data:" + expected_log])
