"""This document contains a flow to clean a given pandas dataframe"""

from prefect import flow
import pandas as pd

flow(name="Clean data flow", description="Cleans and rename columns in the DataFrame.")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and rename columns in the DataFrame.

    Parameters:
    df (pd.DataFrame): The original DataFrame.

    Returns:
    pd.DataFrame: The cleaned DataFrame with renamed columns.
    """
    df = df.drop(columns=["time"])
    df = df.rename(
        columns={
            "date": "Date",
            "priceUsd": "PriceUSD",
            "circulatingSupply": "CirculatingSupply",
        }
    )
    return df
