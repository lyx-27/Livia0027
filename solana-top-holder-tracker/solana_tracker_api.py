import requests
import json
from config import SOLANA_TRACKER_API_KEY

BASE_URL = "https://data.solanatracker.io"

def get_top_holders(token_address: str):
    endpoint = f"/tokens/{token_address}/holders/top"
    headers = {
        "x-api-key": SOLANA_TRACKER_API_KEY
    }
    url = BASE_URL + endpoint

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if 'data' in data and 'items' in data['data']:
                holders = data['data']['items']
                return holders
            elif 'items' in data:
                holders = data['items']
                return holders
            else:
                return data
        else:
            return None
            
    except requests.exceptions.RequestException:
        return None

if __name__ == "__main__":
    pass
