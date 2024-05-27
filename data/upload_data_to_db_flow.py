from prefect import flow, task
import pandas as pd
from sqlalchemy import create_engine

@flow(
    name="Upload df to {schema}.{table_name}",
    description="Upload a DataFrame to a specified schema in a PostgreSQL database.",
)
def upload_data_to_database(
    df: pd.DataFrame,
    schema: str,
    table_name: str,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: int,
    db_name: str,
) -> None:
    """
    Upload a DataFrame to a specified schema in a PostgreSQL database.

    Parameters:
    df (pandas.DataFrame): The DataFrame to upload.
    schema (str): The target schema in the database.
    table_name (str): The name of the target table.
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
        name=table_name, con=engine, schema=schema, if_exists="append", index=False
    )
