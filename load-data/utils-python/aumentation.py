import csv
import io
import random
import os
import datetime
from collections import defaultdict
from faker import Faker

# Initialize faker
fake = Faker()

# Default paths
DEFAULT_INPUT = 'input.csv'
DEFAULT_OUTPUT = 'unnormalized.csv'

# Read orders from CSV
def read_orders(file_path):
    with open(file_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames

# Generate artificial order rows
def generate_artificial_orders(rows, num_to_generate=None, variation_factor=0.15):
    if num_to_generate is None:
        num_to_generate = len(rows)
    max_order_id = max(int(r['order_id']) for r in rows)
    max_customer_id = max(int(r['customer_id']) for r in rows)

    # Patterns by cuisine
    restaurant_cuisine = {r['restaurant_name']: r['cuisine_type'] for r in rows}
    costs = defaultdict(list)
    prep_times = defaultdict(list)
    delivery_times = defaultdict(list)
    for r in rows:
        costs[r['cuisine_type']].append(float(r['cost_of_the_order']))
        prep_times[r['cuisine_type']].append(int(r['food_preparation_time']))
        delivery_times[r['cuisine_type']].append(int(r['delivery_time']))

    cuisine_cost_ranges = {
        c: (sum(v)/len(v)*(1-variation_factor), sum(v)/len(v)*(1+variation_factor))
        for c, v in costs.items()
    }
    day_ratings = {
        'Weekend': ['Not given', 'Not given', 4, 5],
        'Weekday': [5, 4, 5, 'Not given']
    }

    new = []
    for _ in range(num_to_generate):
        template = random.choice(rows).copy()
        record = template.copy()

        max_order_id += random.randint(1, 5)
        max_customer_id += random.randint(1, 5)
        record['order_id'] = str(max_order_id)
        record['customer_id'] = str(max_customer_id)

        # Random restaurant swap
        if random.random() > 0.7:
            rname, ctype = random.choice(list(restaurant_cuisine.items()))
            record['restaurant_name'], record['cuisine_type'] = rname, ctype

        # Cost variation
        cuisine = record['cuisine_type']
        if cuisine in cuisine_cost_ranges:
            lo, hi = cuisine_cost_ranges[cuisine]
            record['cost_of_the_order'] = str(round(random.uniform(lo, hi), 2))

        # Day flip
        if random.random() < 0.4:
            record['day_of_the_week'] = (
                'Weekday' if template['day_of_the_week'] == 'Weekend' else 'Weekend'
            )

        # Rating
        record['rating'] = str(random.choice(day_ratings[record['day_of_the_week']]))

        # Prep time
        if cuisine in prep_times and prep_times[cuisine]:
            avg_prep = sum(prep_times[cuisine]) / len(prep_times[cuisine])
            record['food_preparation_time'] = str(max(1, int(avg_prep + random.randint(-3, 3))))

        # Delivery time
        if cuisine in delivery_times and delivery_times[cuisine]:
            avg_del = sum(delivery_times[cuisine]) / len(delivery_times[cuisine])
            record['delivery_time'] = str(max(10, int(avg_del + random.randint(-4, 4))))

        new.append(record)
    return new

# Enrich and flatten function
def enrich_and_flatten(rows):
    # Customer enrichment
    customer_ids = set(r['customer_id'] for r in rows)
    customer_info = {}
    for cid in customer_ids:
        customer_info[cid] = {
            'cust_first_name': fake.first_name(),
            'cust_last_name': fake.last_name(),
            'cust_email': fake.email(),
            'cust_phone': fake.phone_number(),
            'cust_address': fake.street_address(),
            'cust_city': fake.city(),
            'cust_registration_date': fake.date_between('-5y','today').isoformat()
        }
    # Restaurant enrichment
    restaurant_names = set(r['restaurant_name'] for r in rows)
    price_map = { '$':['$','$$'], '$$':['$$','$$$'], '$$$':['$$$','$$$$'], '$$$$':['$$$$'] }
    restaurant_info = {}
    for name in restaurant_names:
        cuisine = next(r['cuisine_type'] for r in rows if r['restaurant_name']==name)
        pr = random.choice(price_map.get(cuisine, ['$$']))
        rating_avg = round(random.uniform(3.0,4.9), 2)
        open_h = f"{random.randint(7,16)}:00"
        close_h = f"{random.randint(20,23)}:00"
        restaurant_info[name] = {
            'rest_address': fake.street_address(),
            'rest_city': fake.city(),
            'rest_phone': fake.phone_number(),
            'rest_website': f"www.{name.lower().replace(' ','')}.com",
            'rest_price_range': pr,
            'rest_rating_avg': rating_avg,
            'rest_opening_hour': open_h,
            'rest_closing_hour': close_h,
            'rest_established_date': fake.date_between('-10y','-1y').isoformat()
        }
    # Day flags
    days_info = {
        'Weekday': {'is_weekend': False, 'is_holiday': False},
        'Weekend': {'is_weekend': True, 'is_holiday': random.random()<0.1}
    }
    # Delivery persons
    delivery_persons = [
        {
            'del_id': i,
            'del_first_name': fake.first_name(),
            'del_last_name': fake.last_name(),
            'del_phone': fake.phone_number(),
            'del_email': fake.email(),
            'del_vehicle': random.choice(['car','motorcycle','bicycle','scooter','on foot']),
            'del_hire_date': fake.date_between('-3y','today').isoformat(),
            'del_rating': round(random.uniform(3.0,5.0),2)
        } for i in range(1,51)
    ]
    # Flatten
    flat = []
    for r in rows:
        dp = random.choice(delivery_persons)
        cost = float(r['cost_of_the_order'])
        rating_val = None if r['rating']=='Not given' else float(r['rating'])
        if rating_val is None:
            pct = random.uniform(0,0.1)
        elif rating_val >= 4:
            pct = random.uniform(0.15,0.25)
        else:
            pct = random.uniform(0.05,0.15)
        tip = round(cost * pct, 2)
        rec = {
            **r,
            **customer_info[r['customer_id']],
            **restaurant_info[r['restaurant_name']],
            **days_info[r['day_of_the_week']],
            **{k: v for k, v in dp.items() if k != 'del_id'},
            'delivery_person_id': dp['del_id'],
            'tip_amount': tip
        }
        flat.append(rec)
    return flat

# Write CSV output
def write_csv(rows, out_file):
    if not rows:
        return
    with open(out_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f'Enriched CSV written to {out_file}')

# Main execution with argument parsing
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Augment and enrich orders CSV into a single unnormalized file')
    parser.add_argument('--input', '-i', default=DEFAULT_INPUT, help='Path to input orders CSV')
    parser.add_argument('--output', '-o', default=DEFAULT_OUTPUT, help='Path for output enriched CSV')
    parser.add_argument('--count', '-c', type=int, default=None,
                        help='Number of artificial entries to generate (defaults to same as input rows)')
    parser.add_argument('--variation', '-v', type=float, default=0.15,
                        help='Variation factor for cost ranges (default 0.15)')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        exit(1)

    orig_rows, _ = read_orders(args.input)
    artificial = generate_artificial_orders(orig_rows, num_to_generate=args.count, variation_factor=args.variation)
    combined = orig_rows + artificial
    flat = enrich_and_flatten(combined)
    write_csv(flat, args.output)
