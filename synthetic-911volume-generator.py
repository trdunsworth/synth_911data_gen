import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_synthetic_data(num_rows, start_date=None):
    """
    Generate synthetic data with controlled distributions
    
    Parameters:
    - num_rows: Number of rows to generate
    - start_date: Optional start date for the date column (defaults to today if not specified)
    
    Returns:
    - pandas DataFrame with generated synthetic data
    """
    # Set a random seed for reproducibility
    np.random.seed(42)
    
    # Generate date column
    if start_date is None:
        start_date = datetime.now()
    
    dates = [start_date + timedelta(days=i) for i in range(num_rows)]
    
    # Example of generating an integer column with normal distribution
    # Parameters: mean, standard deviation, min, max
    def generate_normal_int_column(mean, std, min_val, max_val):
        # Generate normal distribution
        values = np.random.normal(mean, std, num_rows)
        
        # Clip values to specified min and max
        values = np.clip(values, min_val, max_val)
        
        # Round to integers
        return np.round(values).astype(int)
    
    # Example of generating float columns with uniform distribution within specified range
    def generate_float_column(min_val, max_val):
        # Generate uniform distribution within specified range
        values = np.random.uniform(min_val, max_val, num_rows)
        
        # Round to 4 decimal places
        return np.round(values, 4)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        
        # Example integer columns with different distributions
        'IntColumn1': generate_normal_int_column(mean=50, std=10, min_val=0, max_val=100),
        'IntColumn2': generate_normal_int_column(mean=75, std=15, min_val=25, max_val=125),
        
        # Example float columns within specified range
        'FloatColumn1': generate_float_column(0.8200, 1.0000),
        'FloatColumn2': generate_float_column(0.8200, 1.0000)
    })
    
    return df

# Example usage
num_rows = 100
synthetic_data = generate_synthetic_data(num_rows)

# Display first few rows and basic statistics
print(synthetic_data.head())
print("\nColumn Statistics:")
print(synthetic_data.describe())
