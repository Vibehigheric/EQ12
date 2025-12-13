import time
import requests

def get_bitcoin_price():
    try:
        response = requests.get('https://api.coindesk.com/v1/bpi/currentprice/BTC.json')
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        return data['bpi']['USD']['rate']
    except (requests.HTTPError, KeyError) as e:
        print(f'Error fetching Bitcoin price: {e}')
        return None

def main():
    while True:
        price = get_bitcoin_price()
        if price is not None:
            print(f'Current Bitcoin price: ${price}')
        time.sleep(10)

if __name__ == '__main__':
    main()
