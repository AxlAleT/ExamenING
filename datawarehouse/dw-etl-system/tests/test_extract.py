import unittest
from src.etl.extract import extract_data

class TestExtract(unittest.TestCase):

    def test_extract_data(self):
        # Assuming extract_data returns a list of dictionaries
        result = extract_data()
        self.assertIsInstance(result, list)
        if result:
            self.assertIsInstance(result[0], dict)

if __name__ == '__main__':
    unittest.main()