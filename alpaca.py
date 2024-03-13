import alpaca_trade_api as tradeapi
import requests
import sqlite3
from datetime import datetime
import time


API_KEY = 'xxx'
API_SECRET = 'xxx'
APCA_API_BASE_URL = 'https://paper-api.alpaca.markets'  
client = tradeapi.REST(API_KEY, API_SECRET, base_url=APCA_API_BASE_URL, api_version='v2')
cryptos = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']

def get_trading_price(crypto):
    endpoint = f'https://api.dex-trade.com/v1/public/ticker?pair={crypto}'
    response = requests.get(endpoint)
    trades = response.json()
    current_price = float(trades['data']['last'])
    return current_price



def buy(crypto, amount):
    account = client.get_account()
    cash = float(account.cash)
    current_price = get_trading_price(crypto)
    if(current_price * float(amount) >= cash):
        return "Not enough money to purchase"
    
    try:
        client.submit_order(
            symbol=crypto[:-1], # remove the t at the end of each crypto string
            qty=amount,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        print("Order submitted successfully!")
    except Exception as e:
        print("Failed to submit order:", e)


#sell all holdings
def sell(symbol):
    coin = symbol[:-1]
    try:
        client.close_position(coin)
        print(f"Successfully sold all {symbol}")
    except Exception as e:
        print("Failed to submit order:", e)


def get_crypto(cursor, conn):
    for crypto in cryptos:
        endpoint = f'https://api.dex-trade.com/v1/public/trades?pair={crypto}'
        response = requests.get(endpoint)
        trades = response.json()
        trades_data = trades['data']

        buys = 0
        buy_volume = 0
        sells = 0
        sell_volume = 0
        for item in trades_data:
            if(item['type'] == 'BUY'):
                buy_volume += item['volume']
                buys += 1
            else:
                sell_volume += item['volume']
                sells += 1
        cursor.execute("""
                          INSERT INTO crypto (Crypto, Time, Buys, Sells, Buy_Volume, Sell_Volume)
                          VALUES (?, ?, ?, ?, ?, ?)
            """, (crypto, datetime.now(), buys, sells, buy_volume, sell_volume))
        conn.commit()
        
def get_total_buys_sells(crypto, cursor):
    cursor.execute("""
        SELECT
            crypto,
            SUM(Buys) AS Total_Buys,
            SUM(Sells) AS Total_Sells
        FROM
            crypto
        WHERE
            crypto = ?
    """, (crypto,)) 

    result = cursor.fetchone()

    return result

def get_total_volume(crypto, cursor):
    cursor.execute("""
        SELECT
            crypto,
            SUM(Buys) AS Total_Buys,
            SUM(Sells) AS Total_Sells
        
        FROM
            crypto
        WHERE
            crypto = ?
    """, (crypto,))
    result = cursor.fetchone()
    return result


def main():
    conn = sqlite3.connect('crypto.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS crypto(Crypto, Time, Buys, Sells, Buy_Volume, Sell_Volume)")
    loop = 0
    while True:
        get_crypto(cursor, conn)
        loop += 1
        if(loop == 5):
            for crypto in cryptos:
                total = get_total_buys_sells(crypto, cursor)
                if(total[1] > total[2]):
                    buys = get_total_volume(crypto, cursor)
                    average_buys = buys[1]/125 #divide by 125 as data is stored 5 times with 25 transactions each time
                    buy(crypto, average_buys)
                else:
                    sell(crypto)

            loop = 0
            cursor.execute('DELETE FROM crypto') #clear all entries after 5 loops
            conn.commit()

 
        time.sleep(120)




    conn.close()


main()
