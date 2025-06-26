# Data Warehouse ETL System

This project is an ETL (Extract, Transform, Load) system designed for managing a data warehouse. It provides a structured approach to extract data from various sources, transform it into a suitable format, and load it into a data warehouse for analysis.

## Project Structure

```
dw-etl-system
├── src
│   ├── config          # Configuration files for database and settings
│   ├── etl            # ETL process modules (extract, transform, load)
│   ├── models         # Data models for dimensions and facts
│   ├── utils          # Utility functions for database operations and logging
│   ├── schema         # SQL schema for the data warehouse
│   └── main.py        # Entry point for the application
├── tests              # Unit tests for the ETL process
├── data               # Directories for raw and processed data
├── logs               # Directory for log files
├── requirements.txt   # Project dependencies
├── setup.py           # Packaging and dependency management
├── .env.example       # Example environment variables
└── README.md          # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd dw-etl-system
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables by copying `.env.example` to `.env` and updating the values accordingly.

## Usage

To run the ETL process, execute the following command:
```
python src/main.py
```

## Testing

To run the tests, use:
```
pytest tests/
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.