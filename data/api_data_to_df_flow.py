"""
This document contains a flow to convert coincap api data to a pandas dataframe
"""

import json
from typing import Any, Dict, List, Optional
import pandas as pd
from prefect import flow, task


@task(
    name="Convert api data to json",
    description="Convert a JSON string to a list of data dictionaries.",
)
def convert_data_to_json(json_data_string: str) -> Optional[List[Dict[str, Any]]]:
    """
    Convert a JSON string to a list of data dictionaries.

    Parameters:
    json_data_string (str): A JSON string containing the data.

    Returns:
    Optional[List[Dict[str, Any]]]: A list of dictionaries
    representing the data if successful, None otherwise.
    """
    try:
        json_data = json.loads(json_data_string)
        return json_data.get("data", None)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


@task(
    name="Convert json to pandas dataframe",
    description="Convert a list of data dictionaries to a pandas DataFrame.",
)
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


@flow(
    name="Convert API data to pandas dataframe",
    description="This function takes a JSON string containing \
    CoinCap API data and converts it into a pandas DataFrame.",
)
def api_data_to_df(api_data_string: str) -> pd.DataFrame:
    """
    Convert API data from CoinCap in JSON format to a
    pandas DataFrame.

    This function takes a JSON string containing CoinCap API data and
    converts it into a pandas DataFrame.
    It consists of two main steps:
    1. Converting the JSON string to a list of dictionaries using `convert_data_to_json`.
    2. Converting the list of dictionaries to a pandas DataFrame
    with appropriate data types using `convert_json_to_df`.

    Parameters:
    api_data_string (str): A JSON string containing CoinCap API data.

    Returns:
    None: This function doesn't return anything.
    The pandas DataFrame is created within the function.
          However, it can be assigned to a variable when called.

    Example:
    ```
    api_data_string = '
    {"data":
        [
            {
            "time": 1621484785890,
            "date": "2022-05-20",
            "priceUsd": "0.8",
            "circulatingSupply": "1000000"
            }
        ]
    }'
    api_data_to_df(api_data_string)
    ```
    """
    json_data = convert_data_to_json(api_data_string)
    dataframe = convert_json_to_df(json_data)
    return dataframe
