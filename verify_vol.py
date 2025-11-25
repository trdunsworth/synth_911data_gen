import pandas as pd
import numpy as np
from synthvolgen import generate_synthetic_data
import os

def verify_synthvolgen():
    print("Running generate_synthetic_data...")
    try:
        df = generate_synthetic_data(num_rows=100)
    except Exception as e:
        print(f"FAILED: Execution error: {e}")
        return

    print(f"Generated {len(df)} records.")
    
    # Check columns
    expected_cols = ['Date', 'Recd_911', 'Ab_9111', 'Recd_Admin', 'Ab_Admin', 'Outbound', 'pct_15', 'pct_20']
    missing_cols = [col for col in expected_cols if col not in df.columns]
    
    if missing_cols:
        print(f"FAILED: Missing columns: {missing_cols}")
    else:
        print("PASSED: All columns present.")
        
    # Check pct_20 logic
    # Logic: if pct_15 == 1.0000, then pct_20 == 1.0000
    # else pct_20 > pct_15
    
    mask_100 = df['pct_15'] == 1.0000
    if not df.loc[mask_100, 'pct_20'].eq(1.0000).all():
        print("FAILED: pct_20 logic for pct_15=1.0000 is incorrect.")
    else:
        print("PASSED: pct_20 logic for pct_15=1.0000 is correct.")
        
    mask_not_100 = df['pct_15'] < 1.0000
    if not (df.loc[mask_not_100, 'pct_20'] >= df.loc[mask_not_100, 'pct_15']).all():
         print("FAILED: pct_20 logic for pct_15<1.0000 is incorrect (should be >= pct_15).")
    else:
         print("PASSED: pct_20 logic for pct_15<1.0000 is correct.")

    print("Verification complete.")

if __name__ == "__main__":
    verify_synthvolgen()
