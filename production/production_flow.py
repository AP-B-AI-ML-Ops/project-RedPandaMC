from datetime import datetime, timedelta
from mlflow.tracking import MlflowClient
from sqlalchemy import create_engine
import mlflow
import numpy as np
import pandas as pd
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

def get_data_from_database(
    schema: str,
    table_name: str,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: int,
    db_name: str,
) -> pd.DataFrame:
    """
    Fetch data from a database table and return it as a pandas DataFrame.

    Parameters:
    schema (str): The schema name.
    table_name (str): The table name.
    db_user (str): The database user.
    db_password (str): The database password.
    db_host (str): The database host.
    db_port (int): The database port.
    db_name (str): The database name.

    Returns:
    pd.DataFrame: The data from the specified table.
    """
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)
    query = f"SELECT * FROM {schema}.{table_name}"
    df = pd.read_sql_query(query, con=engine)

    return df



def prepare_future_prices_to_database(
    num_values: int,
    interval: str,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: int,
    db_name: str,
):
    db_params = {
        "dbname": db_name,
        "user": db_user,
        "password": db_password,
        "host": db_host,
        "port": db_port,
    }

    def get_last_date(cursor):
        cursor.execute('SELECT MAX("Date") FROM recent.recent_data')
        return cursor.fetchone()[0]

    def generate_future_dates(last_date, interval, num_values):
        future_dates = []
        current_date = last_date
        for _ in range(num_values):
            current_date += INTERVAL_MAP[interval]
            future_dates.append(current_date)
        return future_dates

    def insert_predicted_data(cursor, future_dates):
        insert_query = 'INSERT INTO prediction.predicted_data ("PriceUSDPredicted", "FutureDate") VALUES (%s, %s)'
        for date in future_dates:
            cursor.execute(insert_query, (0, date))

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


def get_production_model():
    client = MlflowClient()
    model_name = "CryptoPredictor"
    alias = "Production"

    model_version = client.get_model_version_by_alias(name=model_name, alias=alias)

    model_uri = f"models:/{model_name}/{model_version.version}"
    model = mlflow.pyfunc.load_model(model_uri)

    return model


def predict_future_prices(model, seq_length:int=12):
    # this is fucked create sequences needs to have a df that gets updated 
    # all the time everytime you do a prediction
    def create_sequences(data, seq_length):
        xs, ys = [], []
        for i in range(len(data) - seq_length):
            x = data[i : (i + seq_length)]
            y = data[i + seq_length]
            xs.append(x)
            ys.append(y)
        return np.array(xs), np.array(ys)
    
    # TODO: change this whole function
    




def write_future_prices_to_database():
    pass
