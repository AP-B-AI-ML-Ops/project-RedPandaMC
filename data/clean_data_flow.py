"""This document contains a flow to clean a given pandas dataframe"""
import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and rename columns in the DataFrame.

    Parameters:
    df (pd.DataFrame): The original DataFrame.

    Returns:
    pd.DataFrame: The cleaned DataFrame with renamed columns.
    """
    df = df.drop(columns=["time"])
    df = df.rename(columns={"date": "Date", "priceUsd": "PriceUSD", "circulatingSupply": "CirculatingSupply"})
    return df