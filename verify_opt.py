import sys
import os
import pandas as pd
import numpy as np
from opt_synth911gen import generate_911_data

def verify_output():
    print("Running generate_911_data...")
    try:
        df, call_takers, dispatchers = generate_911_data(num_records=1000)
    except Exception as e:
        print(f"FAILED: Execution error: {e}")
        return

    print(f"Generated {len(df)} records.")
    
    # Check columns
    expected_cols = [
        "call_id", "agency", "event_time", "day_of_year", "week_no", "hour", 
        "day_night", "dow", "shift", "shift_part", "problem", "address", 
        "priority_number", "call_taker", "call_reception", "dispatcher", 
        "queue_time", "dispatch_time", "phone_time", "ack_time", "enroute_time", 
        "on_scene_time", "process_time", "total_time", "time_call_queued", 
        "time_call_dispatched", "time_call_acknowledged", "time_call_disconnected", 
        "time_unit_enroute", "time_call_closed"
    ]
    
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        print(f"FAILED: Missing columns: {missing_cols}")
    else:
        print("PASSED: All columns present.")

    # Check shift values
    shifts = df["shift"].unique()
    if not all(s in ["A", "B", "C", "D"] for s in shifts):
        print(f"FAILED: Invalid shift values: {shifts}")
    else:
        print("PASSED: Shift values valid.")

    # Check shift parts
    parts = df["shift_part"].unique()
    if not all(p in ["EARLY", "MIDS", "LATE"] for p in parts):
        print(f"FAILED: Invalid shift parts: {parts}")
    else:
        print("PASSED: Shift parts valid.")

    # Check day/night
    dn = df["day_night"].unique()
    if not all(d in ["DAY", "NIGHT"] for d in dn):
        print(f"FAILED: Invalid day_night values: {dn}")
    else:
        print("PASSED: Day/Night values valid.")

    # Check for nulls in critical columns
    null_cols = df.columns[df.isnull().any()].tolist()
    if null_cols:
        print(f"WARNING: Null values found in: {null_cols}")
        # problem might be null if agency is not LAW/FIRE/EMS (but it should be)
    else:
        print("PASSED: No null values found.")

    print("Verification complete.")

if __name__ == "__main__":
    verify_output()
