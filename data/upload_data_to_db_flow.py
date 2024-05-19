import json
import pandas as pd
import os
import psycopg2
from psycopg2 import OperationalError, sql


def convert_data_to_json(json_data_string: str):
    try:
        json_data : any = json.loads(json_data_string)
        return json_data["data"]
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def convert_json_to_df(json_data):
    df = pd.DataFrame(json_data)
    
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df["date"] = pd.to_datetime(df["date"])
    df["priceUsd"] = pd.to_numeric(df["priceUsd"])
    df["circulatingSupply"] = pd.to_numeric(df["circulatingSupply"])
    df["circulatingSupply"] = df["circulatingSupply"].astype(int)
    
    return df

def clean_data(df):
    df = df.drop(columns=["time"])
    df = df.rename(columns={"date": "Date", "priceUsd": "PriceUSD", 
                            "circulatingSupply": "CirculatingSupply"})
    return df

def prepare_database(sql_file_path, db_user, db_password, db_host, db_port, db_name):
    try:
        if not os.path.exists(sql_file_path):
            raise FileNotFoundError(f"SQL file '{sql_file_path}' does not exist.")

        with open(sql_file_path, encoding='utf-8', mode='r') as sql_f:
            sql_statements = sql_f.read()

        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_statements)
            conn.commit()
            print("Database preparation completed successfully.")
        except psycopg2.Error as e:
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

        

def upload_data_to_database(db_user,db_password,db_host,db_port,db_name):
    engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
    