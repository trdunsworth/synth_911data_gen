import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from faker import Faker
from faker.providers import DynamicProvider
import argparse

fake = Faker()

law_problem_provider = DynamicProvider(
    provider_name="law_problem",
    elements=[
        "TRAFFIC STOP",
        "PARKING COMPLAINT",
        "DISORDERLY CONDUCT",
        "SUSPICIOUS EVENT",
        "MVC",
        "POLICE INFORMATION",
        "ALARM COMMERCIAL",
        "DOMESTIC VIOL",
        "TRESPASSING",
        "ASSIST CITIZEN",
        "PUBLIC SERVICE - LAW",
        "MENTAL HEALTH",
        "NOISE COMPLAINT",
        "LARCENY",
        "DISABLED MOTORIST",
        "ALARM RESIDENTIAL",
        "DRUG COMPLAINT",
        "FLAG DOWN",
        "ASSAULT",
        "GLA",
    ],
)

fire_problem_provider = DynamicProvider(
    provider_name="fire_problem",
    elements=[
        "FIRE ALARM",
        "ELEVATOR",
        "MVC AUTO",
        "GAS LEAK",
        "PUBLIC SERVICE - FIRE",
        "OUTSIDE FIRE",
        "CO ALARM",
        "RESIDENTIAL BUILDING FIRE",
        "HIGHRISE BUILDING FIRE",
        "COMMERCIAL BUILDING FIRE",
        "ODOR OF SMOKE",
        "APPLIANCE FIRE",
        "LOCKOUT",
        "ENTRAPMENT",
        "MVC SCHOOL BUS",
        "WIRES DOWN",
        "HAZMAT",
        "MVC MOTORCYCLE",
    ],
)

ems_problem_provider = DynamicProvider(
    provider_name="ems_problem",
    elements=[
        "ALS EMERGENCY",
        "BLS EMERGENCY",
        "TROUBLE BREATHING ALS",
        "FALL BLS",
        "PUBLIC SERICE EMS",
        "CHEST PAIN ALS",
        "CARDIAC ARREST ALS",
        "ALTERED LOC ALS",
        "UNCONSCIOUS ALS",
        "HEART PROBLEMS ALS",
        "SEIZURE ALS",
        "STROKE ALS",
        "INJURED PERSON BLS",
        "BACK PAIN BLS",
        "MENTAL HEALTH ALS",
        "ASSAULT ALS",
        "DIABETIC EMERGENCY ALS",
        "OVERDOSE ALS",
        "HEADACHE BLS",
        "ALLERGIC REACTION ALS",
        "PSYCHIATRIC EMERGENCY ALS",
    ],
)

address_list = [fake.unique.street_address() for _ in range(2500)]


street_address_provider = DynamicProvider(
    provider_name="street_address", elements=address_list
)


def generate_911_data(num_records=10000):
    def generate_names(num_names=8):
        return [f"{fake.first_name()} {fake.last_name()}" for _ in range(num_names)]

    call_taker_names = {key: generate_names() for key in ["A", "B", "C", "D"]}
    dispatcher_names = {key: generate_names() for key in ["A", "B", "C", "D"]}

    # Define the probabilities for each agency
    probabilities = [0.72, 0.17, 0.11]
    agencies = ["LAW", "EMS", "FIRE"]

    # Generate the agency column with the specified distribution
    agency_choices = np.random.choice(agencies, size=num_records, p=probabilities)

    # Map agency to prefix
    agency_prefix = {"LAW": "L", "EMS": "M", "FIRE": "F"}

    # Generate call_id column with agency-specific prefix
    call_ids_full = [
        f"25-{agency_prefix[agency]}{fake.bothify(text='######')}"
        for agency in agency_choices
    ]

    # Generate datetime column with random dates across 2024-2025
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    end_date = datetime(2025, 12, 31, 23, 59, 59)
    date_range = int((end_date - start_date).total_seconds())
    random_seconds = np.random.randint(0, date_range, size=num_records)
    datetimes_full = [
        start_date + timedelta(seconds=int(sec)) for sec in sorted(random_seconds)
    ]

    # ...rest of your code...

    random_seconds = np.random.randint(0, date_range, size=num_records)
    # Convert numpy integers to Python integers before using in timedelta
    datetimes_full = [
        start_date + timedelta(seconds=int(sec)) for sec in sorted(random_seconds)
    ]

    # Create DataFrame
    df_full = pd.DataFrame(
        {
            "call_id": call_ids_full,
            "agency": agency_choices,
            "event_time": datetimes_full,
        }
    )

    # Add day_of_year column
    df_full["day_of_year"] = df_full["event_time"].dt.dayofyear

    # Add week_no column
    df_full["week_no"] = df_full["event_time"].dt.isocalendar().week

    # Add hour column
    df_full["hour"] = df_full["event_time"].dt.hour

    # Add day_night column based on the hour column
    df_full["day_night"] = df_full["hour"].apply(
        lambda x: "DAY" if 6 <= x <= 17 else "NIGHT"
    )

    # Add dow column with the day of the week in 3-character format
    df_full["dow"] = df_full["event_time"].dt.strftime("%a").str.upper()

    # Define the function to determine the shift
    def determine_shift(row):
        if row["week_no"] % 2 == 0:
            if row["day_night"] == "DAY" and row["dow"] in ["MON", "TUE", "FRI", "SAT"]:
                return "A"
            elif row["day_night"] == "NIGHT" and row["dow"] in [
                "MON",
                "TUE",
                "FRI",
                "SAT",
            ]:
                return "C"
            elif row["day_night"] == "DAY" and row["dow"] in ["WED", "THU", "SUN"]:
                return "B"
            elif row["day_night"] == "NIGHT" and row["dow"] in ["WED", "THU", "SUN"]:
                return "D"
        else:
            if row["day_night"] == "DAY" and row["dow"] in ["WED", "THU", "SUN"]:
                return "A"
            elif row["day_night"] == "NIGHT" and row["dow"] in ["WED", "THU", "SUN"]:
                return "C"
            elif row["day_night"] == "DAY" and row["dow"] in [
                "MON",
                "TUE",
                "FRI",
                "SAT",
            ]:
                return "B"
            elif row["day_night"] == "NIGHT" and row["dow"] in [
                "MON",
                "TUE",
                "FRI",
                "SAT",
            ]:
                return "D"

    # Apply the function to create the shift column
    df_full["shift"] = df_full.apply(determine_shift, axis=1)

    # Define the function to determine the shift_part
    def determine_shift_part(hour):
        if hour in [6, 7, 8, 9, 18, 19, 20, 21]:
            return "EARLY"
        elif hour in [10, 11, 12, 13, 22, 23, 0, 1]:
            return "MIDS"
        else:
            return "LATE"

    # Apply the function to create the shift_part column
    df_full["shift_part"] = df_full["hour"].apply(determine_shift_part)

    # Assign problem type based on agency
    def assign_problem(agency):
        if agency == "LAW":
            return fake.law_problem()
        elif agency == "FIRE":
            return fake.fire_problem()
        elif agency == "EMS":
            return fake.ems_problem()
        else:
            return None

    # Register the dynamic providers with Faker
    fake.add_provider(law_problem_provider)
    fake.add_provider(fire_problem_provider)
    fake.add_provider(ems_problem_provider)

    df_full["problem"] = df_full["agency"].apply(assign_problem)

    # Add address column with a street address

    fake.add_provider(street_address_provider)

    df_full["address"] = [fake.street_address() for _ in range(len(df_full))]

    # Add priority_number column with random integers between 1 and 5
    df_full["priority_number"] = np.random.randint(1, 6, size=len(df_full))

    # Define a function to assign call_taker based on shift
    def assign_call_taker(shift):
        return random.choice(call_taker_names[shift])

    # Apply the function to create the call_taker column
    df_full["call_taker"] = df_full["shift"].apply(assign_call_taker)

    # Define the probabilities for each call reception method
    probabilities_reception = [0.55, 0.20, 0.10, 0.10, 0.05]

    # Define the call reception categories
    reception_methods = ["E-911", "PHONE", "OFFICER", "TEXT", "C2C"]

    # Generate the call_reception column with the specified distribution
    df_full["call_reception"] = np.random.choice(
        reception_methods, size=len(df_full), p=probabilities_reception
    )

    # Define a function to assign dispatcher based on shift
    def assign_dispatcher(shift):
        return random.choice(dispatcher_names[shift])

    # Apply the function to create the dispatcher column
    df_full["dispatcher"] = df_full["shift"].apply(assign_dispatcher)

    mu = 3.5
    sigma = 1.2

    # Generate columns with distributions
    df_full["queue_time"] = np.random.lognormal(
        mean=mu, sigma=sigma, size=len(df_full)
    ).astype(int)
    df_full["queue_time"] = (
        df_full["queue_time"] * 200 / df_full["queue_time"].mean()
    ).astype(int)
    df_full["queue_time"] = df_full["queue_time"].clip(lower=0, upper=90)

    shape, scale = 3.0, 45.0
    df_full["dispatch_time"] = (
        np.random.chisquare(df=2, size=len(df_full)) * 2
    ).astype(int)
    df_full["dispatch_time"] = df_full["dispatch_time"].clip(lower=10, upper=600)

    # More varied phone_time using gamma
    df_full["phone_time"] = np.concatenate(
        [
            np.random.exponential(scale=80, size=int(len(df_full) * 0.8)),  # Fast calls
            np.random.gamma(
                shape=2, scale=200, size=int(len(df_full) * 0.2)
            ),  # Slower calls
        ]
    ).astype(int)

    # ack_time describes the time from the first dispatch to the time the unit marks enroute
    shape, scale = 2.0, 30.0
    df_full["ack_time"] = np.random.gamma(shape, scale, size=len(df_full)).astype(int)
    df_full["ack_time"] = df_full["ack_time"].clip(lower=2, upper=40)

    # More varied enroute_time using gamma with different parameters
    shape, scale = 6.0, 70.0
    df_full["enroute_time"] = np.random.gamma(shape, scale, size=len(df_full)).astype(
        int
    )
    df_full["enroute_time"] = df_full["enroute_time"].clip(lower=300, upper=900)

    # More varied on_scene_time using gamma with heavy tail
    shape, scale = 3.0, 800.0
    df_full["on_scene_time"] = np.random.gamma(shape, scale, size=len(df_full)).astype(
        int
    )
    df_full["on_scene_time"] = df_full["on_scene_time"].clip(lower=300, upper=7200)

    # Add process_time column - sum of queue_time and dispatch_time
    df_full["process_time"] = df_full["queue_time"] + df_full["dispatch_time"]

    df_full["total_time"] = (
        df_full["queue_time"]
        + df_full["dispatch_time"]
        + df_full["ack_time"]
        + df_full["enroute_time"]
        + df_full["on_scene_time"]
    )

    # Time stamp for when call was sent to dispatch queue
    df_full["time_call_queued"] = df_full["event_time"] + pd.to_timedelta(
        df_full["queue_time"], unit="s"
    )

    # Time stamp for when call was dispatched to a unit
    df_full["time_call_dispatched"] = df_full["time_call_queued"] + pd.to_timedelta(
        df_full["dispatch_time"], unit="s"
    )

    # Time stamp for when unit acknowledged the call
    df_full["time_call_acknowledged"] = df_full[
        "time_call_dispatched"
    ] + pd.to_timedelta(df_full["ack_time"], unit="s")

    # Time stamp for when phone call was disconnected
    df_full["time_call_disconnected"] = df_full["event_time"] + pd.to_timedelta(
        df_full["phone_time"], unit="s"
    )

    # Time stamp for when unit arrived on scene
    df_full["time_unit_enroute"] = df_full["time_call_acknowledged"] + pd.to_timedelta(
        df_full["enroute_time"], unit="s"
    )

    # Time stamp for close of call
    df_full["time_call_closed"] = df_full["event_time"] + pd.to_timedelta(
        df_full["total_time"], unit="s"
    )

    # List all your datetime columns
    datetime_cols = [
        "event_time",
        "time_call_queued",
        "time_call_dispatched",
        "time_call_acknowledged",
        "time_call_disconnected",
        "time_unit_enroute",
        "time_call_closed",
    ]

    # Format each datetime column as 'MMMM-YY-DD HH:mm:ss'
    for col in datetime_cols:
        df_full[col] = df_full[col].dt.strftime("%Y-%m-%d %H:%M:%S")

        return df_full, call_taker_names, dispatcher_names


def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Generate 911 Dispatch Synthetic Data")
    parser.add_argument(
        "-n",
        "--num_records",
        type=int,
        default=10000,
        help="Number of records to generate (default: 10000)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Generate data
    df_full, call_taker_names, dispatcher_names = generate_911_data(args.num_records)

    # Save the DataFrame to a CSV file
    csv_path = "./computer_aided_dispatch.csv"
    df_full.to_csv(csv_path, index=False)

    print(f"CSV file saved to {csv_path}")
    print(f"Total records generated: {len(df_full)}")

    # Quick summary statistics of the new columns
    print("\nSummary Statistics for New Columns:")
    print(df_full[["phone_time", "process_time", "total_time"]].describe())

    print("\nCall Taker Names per Shift:")
    for shift, names in call_taker_names.items():
        print(f"Shift {shift}: {names}")

    print("\nDispatcher Names per Shift:")
    for shift, names in dispatcher_names.items():
        print(f"Shift {shift}: {names}")


if __name__ == "__main__":
    main()
