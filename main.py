import requests



# Define the endpoint for retrieving order book data
endpoint = 'https://api.dex-trade.com/v1/public/trades?pair=btcusdt'

# Define the parameters for the request
params = {
    'market': 'BTC_USDT',  # Specify the trading pair (Bitcoin to USDT)
    'depth': 10  # Specify the depth of the order book (number of orders to retrieve)
}

# Make a request to the DEX-Trade API to retrieve order book data
response = requests.get(endpoint)

# Parse the response JSON
order_book_data = response.json()
print(order_book_data)

# Analyze the order book data to determine buying and selling activity
# (Calculate total volume of buy orders vs. sell orders, etc.)
# Your analysis code here...
