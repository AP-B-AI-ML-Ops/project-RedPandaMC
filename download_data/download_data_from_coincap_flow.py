"""This file contains a function which allows for the 
gathering of historic crypto coin related data from coincap API"""
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

def get_bitcoin_data_flow(interval: str, crypto_coin: str = 'bitcoin') -> Optional[Dict[str, Any]]:
    """
    Fetches historical data for a given cryptocurrency.

    Args:
        interval (str): The time interval for data points, e.g., 'm1' for 1 minute, 'h1' for 1 hour, etc.
        crypto_coin (str, optional): The cryptocurrency symbol. Defaults to 'bitcoin'.

    Returns:
        dict or None: A dictionary containing historical data if successful, otherwise None.
    """
    url : str = "https://api.coincap.io/v2/assets/%s/history" % crypto_coin
    
    end_time : int = int(datetime.now().timestamp()) * 1000
    start_time : int = int((datetime.now() - timedelta(weeks=6)).timestamp()) * 1000
    
    params : dict = {
        "interval": interval,
        "start": start_time,
        "end": end_time
    }
    
    response : requests.Response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data : Any = response.json()
        return data
    else:
        print("Failed to fetch data:", response.text)
        return None