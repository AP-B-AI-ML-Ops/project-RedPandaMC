"""
Updates predicition database
"""
from datetime import datetime, timedelta
from typing import List, Optional
import psycopg2

INTERVAL_MAP = {
    "m1": timedelta(minutes=1),
    "m5": timedelta(minutes=5),
    "m15": timedelta(minutes=15),
    "m30": timedelta(minutes=30),
    "h1": timedelta(hours=1),
    "h2": timedelta(hours=2),
    "h6": timedelta(hours=6),
    "h12": timedelta(hours=12),
    "d1": timedelta(days=1),
}

def get_last_date(cursor: psycopg2.extensions.cursor) -> Optional[datetime]:
    """
    Fetch the last date from the recent data table.

    Parameters:
    cursor (psycopg2.extensions.cursor): The database cursor.

    Returns:
    Optional[datetime]: The last date in the recent data table.
    """
    cursor.execute('SELECT MAX("Date") FROM recent.recent_data')
    return cursor.fetchone()[0]


def generate_future_dates(
    last_date: datetime, interval: str, num_values: int
) -> List[datetime]:
    """
    Generate future dates based on the given interval and number of values.

    Parameters:
    last_date (datetime): The last date from which to start generating future dates.
    interval (str): The interval for generating dates.
    num_values (int): The number of future dates to generate.

    Returns:
    List[datetime]: A list of future dates.
    """
    future_dates = []
    current_date = last_date
    for _ in range(num_values):
        current_date += INTERVAL_MAP[interval]
        future_dates.append(current_date)
    return future_dates


def insert_predicted_data(
    cursor: psycopg2.extensions.cursor, future_dates: List[datetime]
) -> None:
    """
    Insert predicted data into the prediction table.

    Parameters:
    cursor (psycopg2.extensions.cursor): The database cursor.
    future_dates (List[datetime]): The future dates to insert into the prediction table.
    """
    insert_query = 'INSERT INTO prediction.predicted_data \
        ("PriceUSDPredicted", "FutureDate") VALUES (%s, %s)'
    for date in future_dates:
        cursor.execute(insert_query, (None, date))


def prepare_future_prices_to_database(
    num_values: int,
    interval: str,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: int,
    db_name: str,
) -> None:
    """
    Prepare future prices and insert them into the database.

    Parameters:
    num_values (int): The number of future values to generate.
    interval (str): The interval for generating future dates.
    db_user (str): The database user.
    db_password (str): The database password.
    db_host (str): The database host.
    db_port (int): The database port.
    db_name (str): The database name.
    """
    db_params = {
        "dbname": db_name,
        "user": db_user,
        "password": db_password,
        "host": db_host,
        "port": db_port,
    }

    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        last_date = get_last_date(cursor)
        future_dates = generate_future_dates(last_date, interval, num_values)
        insert_predicted_data(cursor, future_dates)
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
