# CurrencyConverter

The Currency Converter Microservice provides real-time and historical currency conversion from USD to various supported currencies. It allows you to:

Convert an amount from USD to a target currency using the latest exchange rates.
Retrieve historical exchange rates by specifying a date.

Communication Protocol:

  Protocol: ZeroMQ (Zero Message Queue)

  Socket Type: REQ (Request) / REP (Reply) pattern

  Address: tcp://localhost:5555 (Ensure the microservice is running and listening on this address)


How to Programmatically REQUEST Data:
To request data from the Currency Converter Microservice, send a JSON-formatted message over a ZeroMQ socket with the required parameters.

Request Message Format
Type: JSON object
Parameters:
to_currency (string, required): The target currency code (e.g., "EUR", "JPY"). Must be a valid ISO 4217 currency code.
amount (float, required): The amount in USD to convert.
date (string, optional): The date for historical exchange rates in YYYY-MM-DD format. If omitted or left blank, the latest exchange rates are used.
Example Request
json
Copy code

{

  "to_currency": "EUR",
  
  "amount": 100.0,
  
  "date": "2021-10-01"
  
}

How to Send a Request
Below is an example of how to programmatically send a request to the microservice using Python and ZeroMQ. 

python
Copy code
import zmq

# Create a ZeroMQ context and socket
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")  # Replace with the appropriate address if necessary

# Prepare the request data
request = {
    "to_currency": "EUR",
    "amount": 100.0,
    "date": "2021-10-01"  # Optional: omit or leave blank for latest rates
}

# Send the request to the microservice
socket.send_json(request)
Note: Ensure that the microservice is running and listening on the specified address before sending a request.

How to Programmatically RECEIVE Data
After sending a request, the microservice will respond with a JSON-formatted message containing either the conversion result or an error message.

Response Message Format
Type: JSON object

Successful Response Fields:

converted_amount (float): The converted amount in the target currency.
rate (float): The exchange rate used for the conversion.
date (string): The date of the exchange rate used (either the provided date or "latest").
Error Response Fields:

error (string): A message describing the error.

Example Successful Response
json
Copy code
{
  "converted_amount": 85.96,
  "rate": 0.8596,
  "date": "2021-10-01"
}
Example Error Response
json
Copy code
{
  "error": "Unsupported currency or no data available for 'XYZ' on '2021-10-01'."
}

How to Receive and Process the Response
Below is an example of how to receive and handle the response from the microservice. You should implement your own error handling as appropriate for your application.

python
Copy code

# Receive the response from the microservice
response = socket.recv_json()

# Process the response
if "converted_amount" in response:
    converted_amount = response["converted_amount"]
    rate = response["rate"]
    date_used = response["date"]
    print(f"On {date_used}, {request['amount']} USD = {converted_amount:.2f} {request['to_currency']}")
    print(f"Exchange Rate: 1 USD = {rate:.4f} {request['to_currency']}")
else:
    error_message = response.get("error", "An unknown error occurred.")
    print(f"Error: {error_message}")
