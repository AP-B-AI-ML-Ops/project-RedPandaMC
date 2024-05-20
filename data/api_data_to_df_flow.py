"""This document contains a flow to convert coincap api data to a pandas dataframe"""
import json
from typing import Any, Dict, List, Optional
import pandas as pd

def convert_data_to_json(json_data_string: str) -> Optional[List[Dict[str, Any]]]:
    """
    Convert a JSON string to a list of data dictionaries.

    Parameters:
    json_data_string (str): A JSON string containing the data.

    Returns:
    Optional[List[Dict[str, Any]]]: A list of dictionaries representing the data if successful, None otherwise.
    """
    try:
        json_data = json.loads(json_data_string)
        return json_data.get("data", None)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


def convert_json_to_df(json_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert a list of data dictionaries to a pandas DataFrame.

    Parameters:
    json_data (List[Dict[str, Any]]): A list of dictionaries representing the data.

    Returns:
    pd.DataFrame: A pandas DataFrame with the appropriate data types.
    """
    df = pd.DataFrame(json_data)
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df["date"] = pd.to_datetime(df["date"])
    df["priceUsd"] = pd.to_numeric(df["priceUsd"])
    df["circulatingSupply"] = pd.to_numeric(df["circulatingSupply"])
    df["circulatingSupply"] = df["circulatingSupply"].astype(int)
    return df

def api_data_to_df(api_data_string: str):
    json_data = convert_data_to_json(api_data_string)
    dataframe = convert_json_to_df(json_data)