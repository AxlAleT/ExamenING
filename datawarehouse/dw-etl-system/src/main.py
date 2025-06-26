from etl.extract import DataExtractor
from etl.transform import DataTransformer
from etl.load import DataLoader
from utils.logging import logger
import argparse
import sys
import time

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="ETL System for Data Warehouse")
    parser.add_argument("--extract-only", action="store_true", help="Only run the extract step")
    parser.add_argument("--transform-only", action="store_true", help="Only run the transform step")
    parser.add_argument("--load-only", action="store_true", help="Only run the load step")
    parser.add_argument("--schema-only", action="store_true", help="Only create the schema")
    return parser.parse_args()

def run_etl_pipeline():
    """Run the complete ETL pipeline."""
    logger.info("Starting ETL pipeline")
    
    start_time = time.time()
    
    # Extract
    extractor = DataExtractor()
    extracted_data = extractor.extract_all()
    logger.info("Data extraction completed")
    
    # Transform
    transformer = DataTransformer()
    transformed_data = transformer.transform_all(extracted_data)
    logger.info("Data transformation completed")
    
    # Load
    loader = DataLoader()
    success = loader.load_all(transformed_data)
    
    if success:
        logger.info("Data loading completed successfully")
    else:
        logger.error("Data loading failed")
        
    end_time = time.time()
    logger.info(f"ETL pipeline completed in {end_time - start_time:.2f} seconds")
    
    return success

def main():
    """Main entry point."""
    args = parse_args()
    
    try:
        if args.schema_only:
            logger.info("Creating schema only")
            loader = DataLoader()
            success = loader.create_schema()
            return 0 if success else 1
            
        if args.extract_only:
            logger.info("Extracting data only")
            extractor = DataExtractor()
            extractor.extract_all()
            return 0
            
        if args.transform_only:
            logger.info("Cannot transform without extracted data")
            return 1
            
        if args.load_only:
            logger.info("Cannot load without transformed data")
            return 1
            
        # Run the complete pipeline
        success = run_etl_pipeline()
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"ETL pipeline failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())