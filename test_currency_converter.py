import zmq

def main():
    # Create a ZeroMQ context
    context = zmq.Context()

    # Create a REQ (request) socket to communicate with the microservice
    print("Connecting to the currency converter microservice...")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")  # Ensure the microservice is listening on this address

    # Prompt the user for input
    to_currency = input("Enter the target currency code (e.g., EUR, JPY): ").upper()
    amount_input = input("Enter the amount in USD to convert: ")
    date_input = input("Enter the date for historical rates in 'YYYY-MM-DD' format (leave blank for latest rates): ")

    # Validate and convert the amount input
    try:
        amount = float(amount_input)
    except ValueError:
        print("Invalid amount entered. Please enter a numeric value.")
        return

    # Prepare the request data
    request = {
        "to_currency": to_currency,
        "amount": amount
    }

    # Include the date in the request if provided
    if date_input.strip():
        request["date"] = date_input.strip()
    else:
        print("No date provided. Using the latest exchange rates.")

    # Send the request to the microservice
    print(f"Sending request: {request}")
    socket.send_json(request)

    # Wait for the response from the microservice
    response = socket.recv_json()
    print(f"Received response: {response}")

    # Process and display the response
    if "converted_amount" in response:
        date = response.get('date', 'latest')
        print(f"On {date}, {amount} USD = {response['converted_amount']:.2f} {to_currency}")
        print(f"Exchange Rate: 1 USD = {response['rate']:.4f} {to_currency}")
    else:
        print(f"Error: {response.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
