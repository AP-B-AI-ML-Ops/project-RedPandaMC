"""
In this document you'll find everything 
needed to use the model to forecast data based on recent data
"""
from typing import Any, List, Optional
from datetime import datetime, timedelta
from mlflow.tracking import MlflowClient
from sqlalchemy import create_engine
import mlflow
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
    future_dates (List[datetime]): The future dates to insert 
    into the prediction table.
    """
    insert_query = 'INSERT INTO prediction.predicted_data \
    ("PriceUSDPredicted", "FutureDate") VALUES (%s, %s)'
    for date in future_dates:
        cursor.execute(insert_query, (None, date))


def upload_prediction_to_database(
    df: pd.DataFrame,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: int,
    db_name: str,
) -> None:
    """
    Upload a DataFrame to a specified schema in a PostgreSQL database.

    Parameters:
    df (pd.DataFrame): The DataFrame to upload.
    db_user (str): Database username.
    db_password (str): Database password.
    db_host (str): Database host.
    db_port (int): Database port.
    db_name (str): Database name.
    """
    engine = create_engine(
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    df.to_sql(
        name="predicted_data",
        con=engine,
        schema="prediction",
        if_exists="replace",
        index=False,
    )


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


def get_production_model() -> Any:
    """
    Fetch the production model from MLflow.

    Returns:
    Any: The production model.
    """
    client = MlflowClient()
    model_name = "CryptoPredictor"
    alias = "Production"

    model_version = client.get_model_version_by_alias(name=model_name, alias=alias)
    model_uri = f"models:/{model_name}/{model_version.version}"
    model = mlflow.pyfunc.load_model(model_uri)

    return model


def predict_future_prices(
    model: Any,
    seq_length: int,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: int,
    db_name: str,
) -> None:
    """
    Predict future prices using the given model and upload the predictions to the database.

    Parameters:
    model (Any): The predictive model.
    seq_length (int): The sequence length for the prediction model.
    db_user (str): The database user.
    db_password (str): The database password.
    db_host (str): The database host.
    db_port (int): The database port.
    db_name (str): The database name.
    """
    recent_df = get_data_from_database(
        "recent", "recent_data", db_user, db_password, db_host, db_port, db_name
    )

    last_date = recent_df.iloc[-1]["Date"]

    while True:
        pred_df = get_data_from_database(
            "prediction",
            "predicted_data",
            db_user,
            db_password,
            db_host,
            db_port,
            db_name,
        )

        pred_df.columns = ["PriceUSD", "Date"]

        combined_data = pd.concat([recent_df, pred_df], ignore_index=True)

        if not combined_data["PriceUSD"].isna().any():
            break

        first_nan_index = combined_data["PriceUSD"].isna().idxmax()
        start_index_sequence = first_nan_index - seq_length

        if start_index_sequence < 0:
            raise ValueError("Sequence length is too long for the available data")

        sequence = combined_data.iloc[start_index_sequence:first_nan_index]["PriceUSD"]

        prediction = model.predict(sequence.values.reshape(1, -1))

        combined_data.at[first_nan_index, "PriceUSD"] = prediction[0]

        updated_pred_df = combined_data[combined_data["Date"] > last_date]
        updated_pred_df.columns = ["PriceUSDPredicted", "FutureDate"]

        upload_prediction_to_database(
            updated_pred_df, db_user, db_password, db_host, db_port, db_name
        )
