"""
This document contains a flow to execute a given sql file
"""

import os

from prefect import flow
from psycopg2 import Error, connect


@flow(
    name="Prepare database",
    description="Prepare the database by executing SQL statements from a file.",
)
def prepare_database(
    sql_file_path: str,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: int,
    db_name: str,
) -> None:
    """
    Prepare the database by executing SQL statements from a file.

    Parameters:
    sql_file_path (str): The path to the SQL file containing the statements.
    db_user (str): Database username.
    db_password (str): Database password.
    db_host (str): Database host.
    db_port (int): Database port.
    db_name (str): Database name.
    """
    try:
        if not os.path.exists(sql_file_path):
            raise FileNotFoundError(f"SQL file '{sql_file_path}' does not exist.")

        with open(sql_file_path, encoding="utf-8", mode="r") as sql_f:
            sql_statements = sql_f.read()

        conn = connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        cursor = conn.cursor()

        try:
            cursor.execute(sql_statements)
            conn.commit()
            print("Database preparation completed successfully.")
        except Error as e:
            conn.rollback()
            print(f"Error executing SQL statements: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    except FileNotFoundError as e:
        print(f"File not found error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
