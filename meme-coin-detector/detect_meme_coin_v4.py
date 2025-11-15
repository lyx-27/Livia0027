import requests
import time
import json
import subprocess
from datetime import datetime, timedelta
import collections

BASE_URL = "https://api.dexscreener.com/latest/dex"

history_h1_volumes = {}

VOLUME_INCREASE_FACTOR = 1.5
MIN_5_MIN_VOLUME = 50000
TOKEN_AGE_THRESHOLD_HOURS = 6
POLLING_INTERVAL_SECONDS = 30

def get_pairs_data_by_chain(chain_id, query=None):
    endpoint = f"{BASE_URL}/search?q={query}&chainId={chain_id}" if query else f"{BASE_URL}/search?q={chain_id}"
    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("pairs", [])
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []

def get_pair_data_by_address(chain_id, pair_address):
    endpoint = f"{BASE_URL}/pairs/{chain_id}/{pair_address}"
    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("pairs", [])
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []

def check_meme_coins_bnb_chain():
    global history_h1_volumes
    current_timestamp = datetime.now()

    print("\nStarting BNB chain meme coin detection...")
    chain_id = "bsc"
    
    queries = ["bnb", "wbnb", "busd", "usdt", "cake", "pancakeswap", "ape", "doge", "shib", "floki"]
    all_pairs = {}

    print("Fetching broad pair data...")
    for q in queries:
        pairs = get_pairs_data_by_chain(chain_id, query=q)
        for pair in pairs:
            pair_address = pair.get("pairAddress")
            if pair_address and pair_address not in all_pairs:
                all_pairs[pair_address] = pair
        time.sleep(0.5)

    user_provided_pair_address = "0xee2f63a49cb190962619183103d25af14ce5f538"
    if user_provided_pair_address not in all_pairs:
        print(f"  Querying specific pair: {user_provided_pair_address}...")
        specific_pair_data = get_pair_data_by_address(chain_id, user_provided_pair_address)
        if specific_pair_data:
            for pair in specific_pair_data:
                if pair.get("chainId") == chain_id:
                    all_pairs[pair.get("pairAddress")] = pair
                    print(f"  Added user pair: {pair.get("baseToken", {}).get("symbol", "?")}/{pair.get("quoteToken", {}).get("symbol", "?")}")
        else:
            print(f"  Failed to get data for user pair {user_provided_pair_address}.")

    print(f"Analyzing {len(all_pairs)} unique pairs.")

    if not all_pairs:
        print("No pair data found for analysis.")
        return
    
    potential_meme_coins = []
    
    for pair_address, pair in all_pairs.items():
        pair_name = f"{pair.get("baseToken", {}).get("symbol", "N/A")}/{pair.get("quoteToken", {}).get("symbol", "N/A")}"
        
        h1_volume = pair.get("volume", {}).get("h1")
        h24_volume = pair.get("volume", {}).get("h24")

        h1_price_change = pair.get("priceChange", {}).get("h1")
        h24_price_change = pair.get("priceChange", {}).get("h24")

        pair_created_at = pair.get("pairCreatedAt")
        token_age_hours = 0
        if pair_created_at:
            try:
                created_dt = datetime.fromtimestamp(pair_created_at / 1000)
                token_age_hours = (current_timestamp - created_dt).total_seconds() / 3600
            except (TypeError, ValueError):
                pass

        if pair_address not in history_h1_volumes:
            history_h1_volumes[pair_address] = collections.deque(maxlen=20)
        
        if h1_volume is not None:
            try:
                h1_volume_float = float(h1_volume)
                history_h1_volumes[pair_address].append((current_timestamp, h1_volume_float))
            except ValueError:
                pass

        core_condition_met = False
        calculated_5_min_volume = 0

        if token_age_hours > TOKEN_AGE_THRESHOLD_HOURS:
            five_minutes_ago = current_timestamp - timedelta(minutes=5)
            old_h1_volume = None
            
            for ts, vol in list(history_h1_volumes[pair_address]):
                if ts <= five_minutes_ago:
                    old_h1_volume = vol
                    break
            
            if h1_volume is not None and old_h1_volume is not None:
                try:
                    h1_volume_float = float(h1_volume)
                    calculated_5_min_volume = h1_volume_float - old_h1_volume

                    if old_h1_volume > 0 and \
                       h1_volume_float > old_h1_volume * VOLUME_INCREASE_FACTOR and \
                       calculated_5_min_volume > MIN_5_MIN_VOLUME:
                        core_condition_met = True
                except ValueError:
                    pass

        auxiliary_condition_met = False
        if h1_price_change is not None and h24_price_change is not None:
            try:
                h1_price_change_float = float(h1_price_change)
                h24_price_change_float = float(h24_price_change)
                if h1_price_change_float > h24_price_change_float and h1_price_change_float > 0:
                    auxiliary_condition_met = True
            except ValueError:
                pass

        if core_condition_met:
            fire_emojis = "🔥🔥🔥🔥🔥" if auxiliary_condition_met else "🔥🔥🔥"
            potential_meme_coins.append({
                "pair_name": pair_name,
                "chain": pair.get("chainId"),
                "dex": pair.get("dexId"),
                "h1_volume": h1_volume,
                "h24_volume": h24_volume,
                "h1_price_change": h1_price_change,
                "h24_price_change": h24_price_change,
                "url": pair.get("url"),
                "fire_emojis": fire_emojis,
                "token_age_hours": token_age_hours,
                "calculated_5_min_volume": calculated_5_min_volume
            })
    
    if potential_meme_coins:
        print("\nPotential meme coins detected on BNB Chain:")
        for coin in potential_meme_coins:
            formatted_h1_volume = f"${coin["h1_volume"]:,.2f}" if coin["h1_volume"] is not None else "N/A"
            formatted_h24_volume = f"${coin["h24_volume"]:,.2f}" if coin["h24_volume"] is not None else "N/A"
            formatted_5_min_volume = f"${coin["calculated_5_min_volume"]:,.2f}" if coin["calculated_5_min_volume"] is not None else "N/A"
            
            formatted_h1_price_change = f"{coin["h1_price_change"]} %" if coin["h1_price_change"] is not None else "N/A"
            formatted_h24_price_change = f"{coin["h24_price_change"]} %" if coin["h24_price_change"] is not None else "N/A"

            print(f"  {coin["fire_emojis"]} Pair: {coin["pair_name"]} (Chain: {coin["chain"]}, DEX: {coin["dex"]})")
            print(f"    Age: {coin["token_age_hours"]:.2f} hours")
            print(f"    1h Volume: {formatted_h1_volume}, 24h Volume: {formatted_h24_volume}")
            print(f"    5min Volume: {formatted_5_min_volume}")
            print(f"    1h Price Change: {formatted_h1_price_change}, 24h Price Change: {formatted_h24_price_change}")
            print(f"    Details: {coin["url"]}")
        print("\n")
    else:
        print("No qualifying meme coins found on BNB Chain.")

if __name__ == "__main__":
    try:
        import requests
        import collections
    except ImportError:
        print("Installing required libraries...")
        subprocess.check_call(["python", "-m", "pip", "install", "requests"])
        import requests
        import collections

    while True:
        check_meme_coins_bnb_chain()
        print(f"\nWaiting {POLLING_INTERVAL_SECONDS} seconds for next check...")
        time.sleep(POLLING_INTERVAL_SECONDS)
