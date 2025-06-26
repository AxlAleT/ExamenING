import unittest
from src.etl.transform import transform_data  # Adjust the import based on the actual function name and parameters

class TestTransform(unittest.TestCase):

    def test_transform_data(self):
        # Sample input data
        input_data = [
            {'customer_id': 1, 'order_cost': 100.0, 'rating': 5},
            {'customer_id': 2, 'order_cost': 150.0, 'rating': 4},
            {'customer_id': 1, 'order_cost': 200.0, 'rating': 5},
        ]
        
        # Expected output data after transformation
        expected_output = [
            {'customer_id': 1, 'total_spent': 300.0, 'avg_rating': 5.0},
            {'customer_id': 2, 'total_spent': 150.0, 'avg_rating': 4.0},
        ]
        
        # Call the transform function
        output_data = transform_data(input_data)
        
        # Assert the output matches the expected output
        self.assertEqual(output_data, expected_output)

if __name__ == '__main__':
    unittest.main()