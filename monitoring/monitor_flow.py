"""
In this doc there are function that are 
used to monitor the models performance
"""

import pandas as pd
from sqlalchemy import create_engine
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report


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


def check_data_drift(
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: int,
    db_name: str,
    threshold: float,
) -> bool:
    """
    Check for data drift between recent and predicted data using Evidently.

    Parameters:
    db_user (str): The database user.
    db_password (str): The database password.
    db_host (str): The database host.
    db_port (int): The database port.
    db_name (str): The database name.
    threshold (float): The threshold for considering data drift as significant.

    Returns:
    bool: True if data drift exceeds the threshold, False otherwise.
    """
    recent_data = get_data_from_database(
        "recent", "recent_data", db_user, db_password, db_host, db_port, db_name
    )
    predicted_data = get_data_from_database(
        "prediction", "predicted_data", db_user, db_password, db_host, db_port, db_name
    )

    recent_data = recent_data.rename(columns={"Date": "Date"})
    predicted_data = predicted_data.rename(
        columns={"PriceUSDPredicted": "PriceUSD", "FutureDate": "Date"}
    )

    comparison_data = pd.merge(
        recent_data, predicted_data, on="Date", suffixes=("_actual", "_predicted")
    )

    report = Report(metrics=[DataDriftPreset()])
    report.run(
        reference_data=comparison_data[["Date", "Price_actual"]],
        current_data=comparison_data[["Date", "Price_predicted"]],
    )

    report_json = report.json()
    drift_score = report_json["metrics"][0]["result"]["drift_score"]

    return drift_score > threshold
