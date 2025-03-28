import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

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
        
        # Generate the date fields.
        'Date': dates,
        
        # Generate the call volume counts,
        'Recd_911': generate_normal_int_column(mean=380, std=70, min_val=250, max_val=500),
        'Ab_9111': generate_normal_int_column(mean=50, std=13, min_val=25, max_val=85),
        'Recd_Admin': generate_normal_int_column(mean=600, std=82, min_val=450, max_val=900),
        'Ab_Admin': generate_normal_int_column(mean=10, std=5, min_val=0, max_val=25),
        'Outbound': generate_normal_int_column(mean=375, std=70, min_val=250, max_val=500),
        'pct_15': generate_float_column(0.8200, 1.0000)
        
    })
    
    df['pct_20'] = df.apply(lambda row: 1.0000 if row['pct_15']== 1.0000
                            else np.round(np.random.uniform(row['pct_15'] + 0.0001, 1.0000), 4), axis=1)
    
    output_path = './911_volume_data.csv'
    df.to_csv(output_path, index=False)
        
    return df

df = generate_synthetic_data(num_rows=366, start_date=datetime(2024, 1, 1))
print("Synthetic data generated and saved to 911_volume_data.csv")