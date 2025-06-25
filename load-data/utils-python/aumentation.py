import csv
import io
import random
import os
import datetime
from collections import defaultdict

# Read from file instead of hardcoded string
def read_data_from_file(file_path):
    rows = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows, reader.fieldnames

# Sample input data as a string (replace with file reading in real scenario)
data = """order_id,customer_id,restaurant_name,cuisine_type,cost_of_the_order,day_of_the_week,rating,food_preparation_time,delivery_time
1477147,337525,Hangawi,Korean,30.75,Weekend,Not given,25,20
1477685,358141,Blue Ribbon Sushi Izakaya,Japanese,12.08,Weekend,Not given,25,23
1477070,66393,Cafe Habana,Mexican,12.23,Weekday,5,23,28"""

# Function to generate artificial data with more options
def generate_artificial_data(rows, num_to_generate=None, variation_factor=0.15):
    if num_to_generate is None:
        num_to_generate = len(rows)  # Default to doubling the dataset
    
    # Find max IDs for incrementing
    max_order_id = max(int(row['order_id']) for row in rows)
    max_customer_id = max(int(row['customer_id']) for row in rows)
    
    # Extract patterns from existing data
    restaurant_cuisine = {row['restaurant_name']: row['cuisine_type'] for row in rows}
    cuisine_costs = defaultdict(list)
    for row in rows:
        cuisine_costs[row['cuisine_type']].append(float(row['cost_of_the_order']))
    
    # Calculate cuisine cost ranges
    cuisine_cost_ranges = {}
    for cuisine, costs in cuisine_costs.items():
        if costs:
            avg_cost = sum(costs) / len(costs)
            cuisine_cost_ranges[cuisine] = (avg_cost * (1-variation_factor), 
                                           avg_cost * (1+variation_factor))
    
    # Day patterns for ratings
    day_ratings = {
        'Weekend': ['Not given', 'Not given', 4, 5],  # Mostly not rated
        'Weekday': [5, 4, 5, 'Not given']             # More likely rated
    }
    
    # Prep and delivery time patterns by cuisine
    cuisine_prep_times = defaultdict(list)
    cuisine_delivery_times = defaultdict(list)
    for row in rows:
        cuisine_prep_times[row['cuisine_type']].append(int(row['food_preparation_time']))
        cuisine_delivery_times[row['cuisine_type']].append(int(row['delivery_time']))
    
    # Generate new entries
    new_rows = []
    for _ in range(num_to_generate):
        # Select a random existing row as template or fully random generation
        if random.random() < 0.7:  # 70% based on existing, 30% more random
            template_row = random.choice(rows).copy()
        else:
            # Create more random entry
            restaurant_name, cuisine_type = random.choice(list(restaurant_cuisine.items()))
            template_row = {
                'restaurant_name': restaurant_name,
                'cuisine_type': cuisine_type,
                'day_of_the_week': random.choice(['Weekday', 'Weekend']),
                # Other fields will be filled in below
            }
            
        # Generate new row
        new_row = template_row.copy()
        
        # Generate new IDs
        max_order_id += random.randint(1, 5)
        max_customer_id += random.randint(1, 5)
        new_row['order_id'] = str(max_order_id)
        new_row['customer_id'] = str(max_customer_id)
        
        # Randomly select restaurant and ensure cuisine type matches
        if random.random() > 0.7:  # 30% chance to change restaurant
            new_row['restaurant_name'] = random.choice(list(restaurant_cuisine.keys()))
            new_row['cuisine_type'] = restaurant_cuisine[new_row['restaurant_name']]
        
        # Modify cost based on cuisine patterns
        cuisine = new_row['cuisine_type']
        if cuisine in cuisine_cost_ranges:
            min_cost, max_cost = cuisine_cost_ranges[cuisine]
            new_row['cost_of_the_order'] = str(round(random.uniform(min_cost, max_cost), 2))
        else:
            # Fallback to simpler variation if cuisine is new
            cost = float(template_row.get('cost_of_the_order', 15.0))
            new_row['cost_of_the_order'] = str(round(cost * random.uniform(0.85, 1.15), 2))
        
        # Flip weekday/weekend with 40% probability
        if random.random() < 0.4:
            new_row['day_of_the_week'] = 'Weekday' if template_row.get('day_of_the_week') == 'Weekend' else 'Weekend'
        
        # Generate rating based on day pattern
        new_row['rating'] = str(random.choice(day_ratings[new_row['day_of_the_week']]))
        
        # Vary times based on cuisine patterns when available
        if cuisine in cuisine_prep_times and cuisine_prep_times[cuisine]:
            avg_prep = sum(cuisine_prep_times[cuisine]) / len(cuisine_prep_times[cuisine])
            new_row['food_preparation_time'] = str(max(1, int(avg_prep + random.randint(-3, 3))))
        else:
            # Fallback
            new_row['food_preparation_time'] = str(max(15, int(template_row.get('food_preparation_time', 25)) + random.randint(-3, 3)))
            
        if cuisine in cuisine_delivery_times and cuisine_delivery_times[cuisine]:
            avg_delivery = sum(cuisine_delivery_times[cuisine]) / len(cuisine_delivery_times[cuisine])
            new_row['delivery_time'] = str(max(10, int(avg_delivery + random.randint(-4, 4))))
        else:
            # Fallback
            new_row['delivery_time'] = str(max(10, int(template_row.get('delivery_time', 20)) + random.randint(-4, 4)))
        
        new_rows.append(new_row)
    
    return new_rows

# Main function to run the augmentation
def augment_data(input_file=None, output_file=None, num_to_generate=None):
    if input_file and os.path.exists(input_file):
        rows, fieldnames = read_data_from_file(input_file)
    else:
        # Fallback to sample data
        reader = csv.DictReader(io.StringIO(data))
        rows = list(reader)
        fieldnames = reader.fieldnames
    
    # Generate new data
    new_rows = generate_artificial_data(rows, num_to_generate)
    
    # Combine original and new data
    all_rows = rows + new_rows
    
    # Output results
    if output_file:
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"Augmented data written to {output_file}")
        return output_file
    else:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
        return output.getvalue()

# Allow script to be run directly
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Augment food order data')
    parser.add_argument('--input', help='Input CSV file path', required=True)
    parser.add_argument('--output', help='Output CSV file path (if not specified, prints to console)')
    parser.add_argument('--count', type=int, help='Number of new entries to generate (defaults to matching input size)')
    
    print("Data Augmentation Tool")
    print("----------------------")
    print("This script creates artificial data based on patterns in your input file.")
    print("The output will be written to a new file (will not override your input).")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        exit(1)
    
    print(f"Reading data from: {args.input}")
    if args.output:
        print(f"Output will be saved to: {args.output}")
    else:
        print("No output file specified. Results will be printed to console.")
        
    if args.count:
        print(f"Generating {args.count} new entries")
    else:
        print("Generating entries matching the size of input file")
    
    result = augment_data(args.input, args.output, args.count)
    if not args.output:
        print(result)
    else:
        print(f"Successfully augmented data. Original entries preserved plus new ones added.")
