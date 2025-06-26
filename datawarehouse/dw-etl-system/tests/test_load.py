import unittest
from src.etl.load import load_data
from src.utils.database import Database

class TestLoadData(unittest.TestCase):

    def setUp(self):
        self.db = Database()
        self.test_data = [
            {
                'customer_id': 1,
                'restaurant_id': 1,
                'delivery_person_id': 1,
                'date_id': 20230101,
                'location_id': 1,
                'time_slot_id': 1,
                'order_date': '2023-01-01',
                'order_time': '12:00:00',
                'order_cost': 25.50,
                'rating': 5,
                'food_preparation_time': 15,
                'delivery_time': 30,
                'total_time': 45
            }
        ]

    def test_load_data(self):
        result = load_data(self.test_data)
        self.assertTrue(result)

    def tearDown(self):
        self.db.cleanup()

if __name__ == '__main__':
    unittest.main()