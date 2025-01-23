import websocket
import ssl
import json
import sqlite3

WEBSOCKET_TICKER_URL = "wss://stream.binance.com:9443/ws/!ticker@arr"
START_AMOUNT = 10.00
START_CURRENCY = "USDT"
COMISSION = 0.001

conn = sqlite3.connect("24hTickerTriangles.db")
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS triangles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_balance REAL,
    ticker_1 TEXT,
    ask_1 REAL,
    bid_1 REAL,
    side_1 TEXT,
    ticker_2 TEXT,
    ask_2 REAL,
    bid_2 REAL,
    side_2 TEXT,
    ticker_3 TEXT,
    ask_3 REAL,
    bid_3 REAL,
    side_3 TEXT,
    profit REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()
cursor = conn.cursor()

def save_triangle(route, profit):
    if route is not None and bool(route):
        ticker_1 = list(route.keys())[0]
        ticker_2 = list(route.keys())[1]
        ticker_3 = list(route.keys())[2]

        ask_1 = route[ticker_1]['ask']
        bid_1 = route[ticker_1]['bid']
        side_1 = route[ticker_1]['side']

        ask_2 = route[ticker_2]['ask']
        bid_2 = route[ticker_2]['bid']
        side_2 = route[ticker_2]['side']

        ask_3 = route[ticker_3]['ask']
        bid_3 = route[ticker_3]['bid']
        side_3 = route[ticker_3]['side']

        conn = sqlite3.connect("24hTickerTriangles.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO triangles (
                start_balance, 
                ticker_1, ask_1, bid_1, side_1, 
                ticker_2, ask_2, bid_2, side_2, 
                ticker_3, ask_3, bid_3, side_3, 
                profit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
            START_AMOUNT,
            ticker_1, ask_1, bid_1, side_1,
            ticker_2, ask_2, bid_2, side_2,
            ticker_3, ask_3, bid_3, side_3,
            profit
        ))

        # Сохранение изменений
        conn.commit()
        conn.close()

def read_socket_message(data):
    symbol_map = {item["s"]: item for item in data}
    for step1 in data:
        if START_CURRENCY not in step1["s"]:
            continue
        search_for1 = step1["s"].replace(START_CURRENCY, '')

        for step3 in data:
            if START_CURRENCY not in step3["s"]:
                continue
            search_for2 = step3["s"].replace(START_CURRENCY, '')

            # Находим второй шаг
            step2_key1 = search_for1 + search_for2
            step2_key2 = search_for2 + search_for1
            step2 = symbol_map.get(step2_key1) or symbol_map.get(step2_key2)

            if step2:
                route = {
                    step1['s']: {
                        "bid": float(step1['b']),
                        "bid_qty": float(step1['B']),
                        "ask": float(step1['a']),
                        "ask_qty": float(step1['A'])
                    },
                    step2['s']: {
                        "bid": float(step2['b']),
                        "bid_qty": float(step2['B']),
                        "ask": float(step2['a']),
                        "ask_qty": float(step2['A'])
                    },
                    step3['s']: {
                        "bid": float(step3['b']),
                        "bid_qty": float(step3['B']),
                        "ask": float(step3['a']),
                        "ask_qty": float(step3['A'])
                    }
                }

                profit, route = get_triangle(route)

                if profit > 0 and len(route) == 3:
                    save_triangle(route, profit)
#                    here save data for analytics

def get_triangle(route):
    stepCurrency = START_CURRENCY
    # result = 1.00
    result = START_AMOUNT
    for currency in list(route.keys()):
        price, side = get_price(stepCurrency, currency, route[currency])
        route[currency]['side'] = side
        stepCurrency = currency.replace(stepCurrency, "")
        result *= price
    profit = result - START_AMOUNT
    return profit, route

def get_price(stepCurrency, trade_pair, trade):
    if trade_pair.endswith(stepCurrency):
        side = 'BUY'
        price = 1 / apply_fee(trade['ask'], True)
    else:
        side = 'SELL'
        price = apply_fee(trade['bid'], False)
    return price, side

def apply_fee(price, is_buy, fee=0.001):
    if is_buy:
        return price * (1 + fee)  # Increase price for buying (ask)
    else:
        return price * (1 - fee)  # Decrease price for selling (bid)



def on_message(ws, message):
    data = json.loads(message)
    read_socket_message(data)

def on_open(ws):
    print("WebSocket connection opened")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_error(ws, error):
    print(f"Error: {error}")

def on_ping(ws, message):
    """Обработка ping: отправка pong с таким же содержимым"""
    print(f"Ping received: {message}")
    ws.send(message, opcode=websocket.ABNF.OPCODE_PONG)

def on_pong(ws, message):
    """Обработка pong"""
    print(f"Pong received: {message}")
def main():

    ws = websocket.WebSocketApp(
        WEBSOCKET_TICKER_URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_ping=on_ping,
        on_pong=on_pong
    )

    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


if __name__ == "__main__":
    main()
