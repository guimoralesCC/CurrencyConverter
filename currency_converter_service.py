import zmq
import requests
import time
import datetime

# Cache to store exchange rates with date as key
exchange_rates_cache = {}
CACHE_DURATION = 3600  # 1 hour in seconds

FRANKFURTER_API_URL = 'https://api.frankfurter.app'

def get_exchange_rates(date=None):
    # Use 'latest' if no date is provided
    date_key = date or 'latest'
    current_time = time.time()

    # Check if rates are cached and still valid
    if (date_key in exchange_rates_cache and
        current_time - exchange_rates_cache[date_key]['timestamp'] < CACHE_DURATION):
        print(f"Using cached rates for {date_key}")
        return exchange_rates_cache[date_key]['rates']

    # Build the API URL
    url = f"{FRANKFURTER_API_URL}/{date_key}"
    params = {'from': 'USD'}

    try:
        print(f"Fetching rates for {date_key}...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if 'rates' in data:
            # Cache the rates with a timestamp
            exchange_rates_cache[date_key] = {
                'rates': data['rates'],
                'timestamp': current_time
            }
            print(f"Rates for {date_key} updated.")
            return data['rates']
        else:
            print(f"Error fetching rates: {data}")
            raise ValueError("Invalid response from API.")
    except Exception as e:
        print(f"Exception while fetching rates for {date_key}: {e}")
        raise e

def main():
    # ZeroMQ context and socket setup
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")  # Listening on port 5555

    print("Currency Converter Microservice is running...")

    while True:
        # Wait for next client request
        message = socket.recv_json()
        print(f"Received request: {message}")

        to_currency = message.get("to_currency")
        amount = message.get("amount")
        date = message.get("date")  # Optional date parameter

        # Validate required parameters
        if not to_currency or amount is None:
            response = {"error": "Missing 'to_currency' or 'amount' in the request."}
            socket.send_json(response)
            continue

        # Validate date format if provided
        if date:
            try:
                datetime.datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                response = {"error": "Invalid date format. Use 'YYYY-MM-DD'."}
                socket.send_json(response)
                continue

        try:
            # Fetch exchange rates (latest or historical)
            rates = get_exchange_rates(date)
            # Check if the requested currency is available
            if to_currency not in rates:
                response = {"error": f"Unsupported currency or no data available for {to_currency} on {date or 'latest'}."}
            else:
                rate = rates[to_currency]
                converted_amount = amount * rate
                response = {
                    "converted_amount": converted_amount,
                    "rate": rate,
                    "date": date or 'latest'
                }
        except Exception as e:
            response = {"error": str(e)}

        # Send the response back to the client
        socket.send_json(response)
        print(f"Sent response: {response}")

if __name__ == "__main__":
    main()
