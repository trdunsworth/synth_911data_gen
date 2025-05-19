#! /usr/bin/env python

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from faker import Faker
from faker.providers import DynamicProvider
import argparse
from PyInquirer import prompt, Validator, ValidationError

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

    # Generate call_id column with agency-specific prefix
    call_ids_full = [
        f"25-{agency_prefix[agency]}{fake.bothify(text='######')}"
        for agency in agency_choices
    ]

    # Generate datetime column with random dates across 2024-2025
    # Set default start and end dates if not provided
    if start_date is None:
        start_date = "2024-01-01"
    if end_date is None:
        end_date = "2024-12-31"

    # Convert start_date and end_date to datetime objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Generate random datetimes within the specified range
    date_range = int((end_date - start_date).total_seconds())
    random_seconds = np.random.randint(0, date_range, size=num_records)
    datetimes_full = [
        start_date + timedelta(seconds=int(sec)) for sec in sorted(random_seconds)
    ]

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
        """
        This is a function to determine the shift based on the week number, day_night, and day of the week (dow).
        The function uses the following logic:
        - If the week number is even:
            - DAY on MON, TUE, FRI, SAT -> A
            - NIGHT on MON, TUE, FRI, SAT -> C
            - DAY on WED, THU, SUN -> B
            - NIGHT on WED, THU, SUN -> D
        - This mirrors an existing shift pattern employed by agencies that use a 12 hour shift schedule.

        Args:
            row (_type_): _description_

        Returns:
           string: This returns the shift based on the logic defined above.
        """
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
        """
        This determines how the shift is divided into parts based on the hour of the day. This breaks a 12-hour shift into 3 parts:

        Args:
            hour (int): This is the hour compoenent of the event_time datetime column.

        Returns:
            string: A descriptor of the shift part based on the hour.
        """
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
        """
        This function assigns a problem type based on the agency type. It uses the Faker library to generate random problems for each agency.

        Args:
            agency (string): This is the agency type (LAW, EMS, FIRE).

        Returns:
            string: A random problem type based on the agency.
        """
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
        """
        This function assigns a call_taker based on the shift. It uses the Faker library to generate random names for each shift.

        Args:
            shift (string): This is the shift type (A, B, C, D).

        Returns:
            string: The name of the call_taker based on the shift.
        """
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
        """
        This function assigns a dispatcher based on the shift. It uses the Faker library to generate random names for each shift.

        Args:
            shift (string): This is the shift type (A, B, C, D).

        Returns:
            string: The name of the dispatcher based on the shift.
        """
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
        np.random.chisquare(df=5, size=len(df_full)) * 2
    ).astype(int)
    df_full["dispatch_time"] = df_full["dispatch_time"].clip(lower=5, upper=600)

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
