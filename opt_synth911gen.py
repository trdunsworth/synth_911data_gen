#! /usr/bin/env python

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from faker import Faker
from faker.providers import DynamicProvider
import argparse
import collections.abc
# Patch for PyInquirer compatibility with Python 3.10+
if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping
from PyInquirer import prompt, Validator, ValidationError
import re

def sanitize_input(user_input):
    # Regular expression to match allowed characters
    pattern = r'^[a-zA-Z0-9\s\-]+$'
    if not re.match(pattern, user_input):
        raise ValueError("Input contains invalid characters. Only letters, numbers, spaces, and hyphens are allowed.")
    return user_input

def main():
    parser = argparse.ArgumentParser(description="Sanitize user input options in synth911gen.py")
    
    # Example of a command-line argument
    parser.add_argument('--option', type=str, required=True, help='User input option')
    
    args = parser.parse_args()
    
    try:
        sanitized_option = sanitize_input(args.option)
        print(f"Sanitized Option: {sanitized_option}")
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()

fake = Faker("en_US")

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

# TODO: Add the ability to switch the faker provider to a different locale.
# TODO: Hook this to a web interface to allow users to generate data on demand.


def generate_911_data(num_records=10000, start_date=None, end_date=None, num_names=8):
    """
    This function generates synthetic 911 dispatch data for a given number of records. This will output a CSV file with the generated data.
    The data includes various fields such as call_id, agency, event_time, day_of_year, week_no, hour, day_night, dow, shift, shift_part, problem, address, priority_number, call_taker, call_reception, dispatcher, queue_time, dispatch_time, phone_time, ack_time, enroute_time, on_scene_time, process_time, total_time and time stamps for various events.

    Args:
        num_records (int, optional): _description_. Defaults to 10000.

        TODO: Add the ability to switch the faker provider to a different locale.
        This will allow for generating data in different languages or formats based on the user's needs.

        This needs to be run with the following setup: python synth911gen.py -n 10000 -s 2024-01-01 -e 2024-12-31 -o computer_aided_dispatch.csv
    """

    def generate_names(num_names=8):
        """
        This function generates a list of random names using the Faker library. The number of names generated is determined by the num_names parameter.
        The names are generated in the format "Last, First". This function is used to create call_taker and dispatcher names for the generated data and conforms to the most commonly used formats.

        Args:
            num_names (int, optional): _description_. Defaults to 8.

        Returns:
            dictionary: This returns a dictionary with keys A, B, C, D and values as lists of names.
        """
        return [f"{fake.last_name()}, {fake.first_name()}" for _ in range(num_names)]

    call_taker_names = {key: generate_names(num_names) for key in ["A", "B", "C", "D"]}
    dispatcher_names = {key: generate_names(num_names) for key in ["A", "B", "C", "D"]}

    # Define the probabilities for each agency
    probabilities = [0.72, 0.17, 0.11]
    agencies = ["LAW", "EMS", "FIRE"]

    # Generate the agency column with the specified distribution
    agency_choices = np.random.choice(agencies, size=num_records, p=probabilities)

    # Map agency to prefix
    agency_prefix = {"LAW": "L", "EMS": "M", "FIRE": "F"}
    
    # Vectorized call_id generation
    # Create an array of prefixes corresponding to the agency choices
    prefixes = np.array([agency_prefix[a] for a in agency_choices])
    # Generate random 6-digit numbers
    random_numbers = np.random.randint(0, 1000000, size=num_records)
    # Format them as strings with leading zeros
    random_numbers_str = [f"{x:06d}" for x in random_numbers]
    call_ids_full = [f"25-{p}{n}" for p, n in zip(prefixes, random_numbers_str)]


    # Generate datetime column with random dates across 2024-2025
    # Set default start and end dates if not provided
    if start_date is None:
        start_date = "2024-01-01"
    if end_date is None:
        end_date = "2024-12-31"

    # Convert start_date and end_date to datetime objects
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Generate random datetimes within the specified range
    date_range = int((end_date - start_date).total_seconds())
    random_seconds = np.random.randint(0, date_range, size=num_records)
    # Sort seconds to simulate chronological order
    random_seconds.sort()
    
    # Vectorized datetime generation
    datetimes_full = start_date + pd.to_timedelta(random_seconds, unit='s')

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
    # Vectorized: 6 <= hour <= 17 is DAY
    df_full["day_night"] = np.where(
        (df_full["hour"] >= 6) & (df_full["hour"] <= 17), "DAY", "NIGHT"
    )

    # Add dow column with the day of the week in 3-character format
    df_full["dow"] = df_full["event_time"].dt.strftime("%a").str.upper()

    # Vectorized Shift Determination
    # Logic:
    # Week even:
    #   DAY & (MON, TUE, FRI, SAT) -> A
    #   NIGHT & (MON, TUE, FRI, SAT) -> C
    #   DAY & (WED, THU, SUN) -> B
    #   NIGHT & (WED, THU, SUN) -> D
    # Week odd:
    #   DAY & (WED, THU, SUN) -> A
    #   NIGHT & (WED, THU, SUN) -> C
    #   DAY & (MON, TUE, FRI, SAT) -> B
    #   NIGHT & (MON, TUE, FRI, SAT) -> D
    
    is_even_week = (df_full["week_no"] % 2 == 0)
    is_day = (df_full["day_night"] == "DAY")
    dow = df_full["dow"]
    group1_days = dow.isin(["MON", "TUE", "FRI", "SAT"])
    group2_days = dow.isin(["WED", "THU", "SUN"])
    
    conditions = [
        is_even_week & is_day & group1_days,      # A
        is_even_week & ~is_day & group1_days,     # C
        is_even_week & is_day & group2_days,      # B
        is_even_week & ~is_day & group2_days,     # D
        ~is_even_week & is_day & group2_days,     # A
        ~is_even_week & ~is_day & group2_days,    # C
        ~is_even_week & is_day & group1_days,     # B
        ~is_even_week & ~is_day & group1_days,    # D
    ]
    choices = ["A", "C", "B", "D", "A", "C", "B", "D"]
    
    df_full["shift"] = np.select(conditions, choices, default="UNKNOWN")

    # Vectorized Shift Part
    # EARLY: 6-9, 18-21
    # MIDS: 10-13, 22-1, 0-1 (so 22, 23, 0, 1)
    # LATE: else (2-5, 14-17)
    
    hour = df_full["hour"]
    early_hours = hour.isin([6, 7, 8, 9, 18, 19, 20, 21])
    mids_hours = hour.isin([10, 11, 12, 13, 22, 23, 0, 1])
    
    df_full["shift_part"] = np.select(
        [early_hours, mids_hours],
        ["EARLY", "MIDS"],
        default="LATE"
    )

    # Assign problem type based on agency
    # Pre-generate lists from providers
    law_problems = law_problem_provider.elements
    fire_problems = fire_problem_provider.elements
    ems_problems = ems_problem_provider.elements
    
    # Vectorized assignment
    # We can use np.select or map, but since we need random choices, we can do this:
    # Generate random indices for each type
    n_law = (df_full["agency"] == "LAW").sum()
    n_fire = (df_full["agency"] == "FIRE").sum()
    n_ems = (df_full["agency"] == "EMS").sum()
    
    law_choices = np.random.choice(law_problems, size=n_law)
    fire_choices = np.random.choice(fire_problems, size=n_fire)
    ems_choices = np.random.choice(ems_problems, size=n_ems)
    
    # Place them in the dataframe
    df_full.loc[df_full["agency"] == "LAW", "problem"] = law_choices
    df_full.loc[df_full["agency"] == "FIRE", "problem"] = fire_choices
    df_full.loc[df_full["agency"] == "EMS", "problem"] = ems_choices

    # Add address column with a street address
    # Use the pre-generated address_list
    df_full["address"] = np.random.choice(address_list, size=len(df_full))

    # Add priority_number column with random integers between 1 and 5
    df_full["priority_number"] = np.random.randint(1, 6, size=len(df_full))

    # Assign call_taker based on shift
    # Vectorized approach:
    # For each shift (A, B, C, D), sample names
    for shift in ["A", "B", "C", "D"]:
        mask = df_full["shift"] == shift
        count = mask.sum()
        if count > 0:
            df_full.loc[mask, "call_taker"] = np.random.choice(call_taker_names[shift], size=count)

    # Define the probabilities for each call reception method
    probabilities_reception = [0.55, 0.20, 0.10, 0.10, 0.05]

    # Define the call reception categories
    reception_methods = ["E-911", "PHONE", "OFFICER", "TEXT", "C2C"]

    # Generate the call_reception column with the specified distribution
    df_full["call_reception"] = np.random.choice(
        reception_methods, size=len(df_full), p=probabilities_reception
    )

    # Assign dispatcher based on shift
    for shift in ["A", "B", "C", "D"]:
        mask = df_full["shift"] == shift
        count = mask.sum()
        if count > 0:
            df_full.loc[mask, "dispatcher"] = np.random.choice(dispatcher_names[shift], size=count)

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

    # dispatch_time
    df_full["dispatch_time"] = (
        np.random.chisquare(df=5, size=len(df_full)) * 2
    ).astype(int)
    df_full["dispatch_time"] = df_full["dispatch_time"].clip(lower=5, upper=600)

    # More varied phone_time using gamma
    # Vectorized generation without concatenation if possible, but concat is fine here
    # To keep it simple and fast, we can generate all at once with a mix, but the original logic split 80/20.
    # Let's keep the logic but optimize if needed. Concat is fast enough.
    n_fast = int(len(df_full) * 0.8)
    n_slow = len(df_full) - n_fast
    
    phone_time_fast = np.random.exponential(scale=80, size=n_fast)
    phone_time_slow = np.random.gamma(shape=2, scale=200, size=n_slow)
    # Shuffle to mix them up since we are concatenating
    phone_times = np.concatenate([phone_time_fast, phone_time_slow])
    np.random.shuffle(phone_times)
    df_full["phone_time"] = phone_times.astype(int)

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


class DateValidator(Validator):
    def validate(self, document):
        try:
            datetime.strptime(document.text, '%Y-%m-%d')
        except ValueError:
            raise ValidationError(
                message='Please enter a valid date in YYYY-MM-DD format',
                cursor_position=len(document.text)
            )


def main():
    """
    This is the main entry point of the script. It provides an interactive command line interface
    to generate 911 dispatch data and saves it to a CSV file.
    """
    questions = [
        {
            'type': 'input',
            'name': 'num_records',
            'message': 'How many records would you like to generate?',
            'default': '10000',
            'validate': lambda val: val.isdigit() and int(val) > 0 or 'Please enter a positive number'
        },
        {
            'type': 'input',
            'name': 'start_date',
            'message': 'Enter start date (YYYY-MM-DD):',
            'default': '2024-01-01',
            'validate': DateValidator
        },
        {
            'type': 'input',
            'name': 'end_date',
            'message': 'Enter end date (YYYY-MM-DD):',
            'default': '2024-12-31',
            'validate': DateValidator
        },
        {
            'type': 'input',
            'name': 'num_names',
            'message': 'How many names would you like to generate per shift?',
            'default': '8',
            'validate': lambda val: val.isdigit() and int(val) > 0 or 'Please enter a positive number'
        },
        {
            'type': 'input',
            'name': 'output_file',
            'message': 'Enter the output file path:',
            'default': 'computer_aided_dispatch.csv'
        }
    ]

    answers = prompt(questions)

    # Generate data with specified number of names
    df_full, call_taker_names, dispatcher_names = generate_911_data(
        num_records=int(answers['num_records']),
        start_date=answers['start_date'],
        end_date=answers['end_date'],
        num_names=int(answers['num_names'])
    )

    # Save the DataFrame to a CSV file
    output_file = answers['output_file']
    df_full.to_csv(output_file, index=False)

    print(f"\nCSV file saved to {output_file}")
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
