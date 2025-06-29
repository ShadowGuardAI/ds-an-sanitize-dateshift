import argparse
import logging
import random
import pandas as pd
from dateutil import parser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description='Shifts dates in a specified column by a random number of days.')
    parser.add_argument('input_file', type=str, help='Path to the input CSV file.')
    parser.add_argument('column_name', type=str, help='Name of the column containing dates.')
    parser.add_argument('output_file', type=str, help='Path to the output CSV file.')
    parser.add_argument('--min_shift', type=int, default=-365, help='Minimum number of days to shift (default: -365).')
    parser.add_argument('--max_shift', type=int, default=365, help='Maximum number of days to shift (default: 365).')
    return parser

def sanitize_date_column(df, column_name, min_shift, max_shift):
    """
    Shifts dates in the specified column by a random number of days.

    Args:
        df (pd.DataFrame): The DataFrame to sanitize.
        column_name (str): The name of the column containing dates.
        min_shift (int): The minimum number of days to shift.
        max_shift (int): The maximum number of days to shift.

    Returns:
        pd.DataFrame: The sanitized DataFrame.
    """
    try:
        # Input validation: check if the column exists
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in the input file.")

        # Input validation: check if min_shift and max_shift are integers
        if not isinstance(min_shift, int) or not isinstance(max_shift, int):
            raise TypeError("min_shift and max_shift must be integers.")

        # Input validation: check if min_shift is less than or equal to max_shift
        if min_shift > max_shift:
            raise ValueError("min_shift must be less than or equal to max_shift.")
            
        # Convert the column to datetime objects, handling potential parsing errors
        def shift_date(date_str):
            try:
                date_obj = parser.parse(date_str)
                shift = random.randint(min_shift, max_shift)
                return date_obj + pd.Timedelta(days=shift)
            except (ValueError, TypeError) as e:
                logging.warning(f"Could not parse date '{date_str}': {e}. Returning original value.")
                return date_str  # Return the original value if parsing fails

        # Apply the date shifting function to the specified column
        df[column_name] = df[column_name].astype(str).apply(shift_date)
        
        return df

    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        raise
    except TypeError as te:
        logging.error(f"TypeError: {te}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise

def main():
    """
    Main function to execute the date shifting process.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        # Read the input CSV file into a DataFrame
        df = pd.read_csv(args.input_file)

        # Sanitize the date column
        sanitized_df = sanitize_date_column(df, args.column_name, args.min_shift, args.max_shift)

        # Write the sanitized DataFrame to the output CSV file
        sanitized_df.to_csv(args.output_file, index=False)

        logging.info(f"Successfully sanitized '{args.column_name}' in '{args.input_file}' and saved to '{args.output_file}'.")

    except FileNotFoundError:
        logging.error(f"Input file '{args.input_file}' not found.")
    except pd.errors.EmptyDataError:
        logging.error(f"Input file '{args.input_file}' is empty.")
    except pd.errors.ParserError:
        logging.error(f"Error parsing input file '{args.input_file}'.  Ensure it's a valid CSV.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

# Usage Examples:
# 1. Basic usage:
#    python main.py input.csv date_column output.csv

# 2. Shift dates by a smaller range:
#    python main.py input.csv date_column output.csv --min_shift -10 --max_shift 10

# 3. Shift dates only into the future:
#    python main.py input.csv date_column output.csv --min_shift 0 --max_shift 365