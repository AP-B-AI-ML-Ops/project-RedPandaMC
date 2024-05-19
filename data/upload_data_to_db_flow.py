import json
import pandas as pd
from sqlalchemy import create_engine

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
    df["PricePerToken"] = df["PriceUSD"] / df["CirculatingSupply"]
    return df

def upload_data_to_db(db_user,db_password,db_port,db_name):
    engine = create_engine(f"postgresql://{db_user}:{db_password}@localhost:{db_port}/{db_name}")