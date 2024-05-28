from typing import Any, List, Optional
from datetime import datetime, timedelta
from mlflow.tracking import MlflowClient
from sqlalchemy import create_engine
from prefect import task, flow
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

@task()
def get_data_from_database(
    schema: str,
    table_name: str,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: int,
    db_name: str,
) -> pd.DataFrame:
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)
    query = f"SELECT * FROM {schema}.{table_name}"
    df = pd.read_sql_query(query, con=engine)
    return df

@task()
def get_last_date(cursor: psycopg2.extensions.cursor) -> Optional[datetime]:
    cursor.execute('SELECT MAX("Date") FROM mlops.recentdata')
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

@task()
def generate_future_dates(
    last_date: datetime, interval: str, num_values: int
) -> List[datetime]:
    future_dates = []
    current_date = last_date
    for _ in range(num_values):
        current_date += INTERVAL_MAP[interval]
        future_dates.append(current_date)
    return future_dates

@task()
def insert_predicted_data(
    cursor: psycopg2.extensions.cursor, future_dates: List[datetime]
) -> None:
    insert_query = 'INSERT INTO mlops.predicteddata ("PriceUSD", "FutureDate") VALUES (%s, %s)'
    for date in future_dates:
        cursor.execute(insert_query, (None, date))

@task()
def upload_prediction_to_database(
    df: pd.DataFrame,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: int,
    db_name: str,
) -> None:
    engine = create_engine(
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    df.to_sql(
        name="predicteddata",
        con=engine,
        schema="mlops",
        if_exists="replace",
        index=False,
    )

@flow()
def prepare_future_prices_to_database(
    num_values: int,
    interval: str,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: int,
    db_name: str,
) -> None:
    db_params = {
        "database": db_name,
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
        if last_date is None:
            raise ValueError("No last date found in the database.")
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

@task()
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

@flow()
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
        "mlops", "recentdata", db_user, db_password, db_host, db_port, db_name
    )

    last_date = recent_df.iloc[-1]["Date"]

    while True:
        pred_df = get_data_from_database(
            "mlops",
            "predicteddata",
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
