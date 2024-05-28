"""
This document contains a flow to clean a given pandas dataframe
"""

import pandas as pd
from prefect import flow


@flow(name="Clean data flow", description="Cleans and rename columns in the DataFrame.")
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and rename columns in the DataFrame.

    Parameters:
    df (pd.DataFrame): The original DataFrame.

    Returns:
    pd.DataFrame: The cleaned DataFrame with renamed columns.
    """
    df = df.drop(columns=["date", "circulatingSupply"])
    df = df.rename(columns={"time": "Time", "priceUsd": "PriceUSD"})
    return df
