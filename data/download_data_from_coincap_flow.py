"""This module provides a function for fetching historical data of a given cryptocurrency from the CoinCap API."""

from prefect import flow, task
import requests
from datetime import datetime
from typing import Optional, Dict, Any


@flow(
    flow_run_name="Get api data from {start_date} to {end_date}",
    retries=3,
    retry_delay_seconds=3,
    description="Fetches historical data for a given cryptocurrency from the CoinCap API.",
)
def get_crypto_data_flow(
    interval: str = "m15",
    crypto_coin: str = "bitcoin",
    start_date: str = "01/01/2021",
    end_date: str = "01/02/2021",
) -> Optional[Dict[str, Any]]:
    """
    Fetches historical data for a given cryptocurrency from the CoinCap API.

    Args:
        interval (str, optional): The time interval for data points. Defaults to 'm15' (15 minutes).
        crypto_coin (str, optional): The cryptocurrency symbol. Defaults to 'bitcoin'.
        start_date (str, optional): The start date for data retrieval in 'dd/mm/yyyy' format. Defaults to '01/01/2021'.
        end_date (str, optional): The end date for data retrieval in 'dd/mm/yyyy' format. Defaults to '01/02/2021'.

    Returns:
        tuple or None: A tuple containing headers and historical data if successful, otherwise None.
    """

    @task(
        description="Send a GET request to the specified URL with provided parameters, headers, and data."
    )
    def get_data(
        url: str, params: dict, headers: dict, data: dict
    ) -> requests.Response:
        """Send a GET request to the specified URL with provided parameters, headers, and data."""
        resp: requests.Response = requests.get(
            url, params=params, headers=headers, data=data
        )
        return resp

    start_timestamp: int = (
        int(datetime.strptime(start_date, "%d/%m/%Y").timestamp()) * 1000
    )
    end_timestamp: int = int(datetime.strptime(end_date, "%d/%m/%Y").timestamp()) * 1000

    url: str = f"https://api.coincap.io/v2/assets/{crypto_coin}/history?"

    params: dict = {
        "interval": interval,
        "start": start_timestamp,
        "end": end_timestamp,
    }

    headers: dict = {}

    payload: dict = {}

    response: requests.Response = get_data(url, params, headers, payload)

    if response.status_code == 200:
        return response.headers, response.text
    else:
        print("Failed to fetch data:", response.text)
        return response.headers, response.text
