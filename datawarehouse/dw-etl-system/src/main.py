from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_data

def main():
    raw_data = extract_data()
    transformed_data = transform_data(raw_data)
    load_data(transformed_data)

if __name__ == "__main__":
    main()