"""This file contains a function which allows for the 
gathering of historic crypto coin related data from coincap API"""
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

def get_crypto_data_flow(interval: str = "m15", crypto_coin: str = "dogecoin") -> Optional[Dict[str, Any]]:
    """
    Fetches historical data for a given cryptocurrency.

    Args:
        interval (str): The time interval for data points, e.g., 'm1' for 1 minute, 'h1' for 1 hour, etc.
        crypto_coin (str, optional): The cryptocurrency symbol. Defaults to 'bitcoin'.

    Returns:
        dict or None: A dictionary containing historical data if successful, otherwise None.
    """
    def get_data(url:str,params:dict,headers:dict,data:dict):
        resp : requests.Response = requests.get(url, params=params, headers=headers,data=data)
        return resp

    url : str = "https://api.coincap.io/v2/assets/%s/history?" % crypto_coin
    
    end_time : int = int(datetime.now().timestamp()) * 1000
    start_time : int = int((datetime.now() - timedelta(weeks=6)).timestamp()) * 1000
    params : dict = {
        "interval": interval,
        "start": start_time,
        "end": end_time
    }

    headers : dict = {}

    payload : dict = {}

    response : requests.Response = get_data(url,params,headers,payload)
    
    if response.status_code == 200:
        return response.headers, response.text
    else:
        print("Failed to fetch data:", response.text)
        return response.headers, response.text