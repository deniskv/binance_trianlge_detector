# Binance Triangle Arbitrage Detector

## Use this script at your own risk

This is a simple script that allows you to find triangle arbitrage opportunities on the Binance spot market.

### How it works

1. Receive a message via websocket
2. Collect possible trading pairs for arbitrage
3. Check profitability with a basic commission
4. Save profitable trading pairs to the database.


### Caveats

If you want to add trading functionality to this script, make sure that your orders are correspond to a following Binance order validation rules:

- Ticker MIN/MAX Notional
- Ticker MIN/MAX Limit
- Precision

Bear in mind, that Binance are usual perform market ordrers for 0.1-0.5 sec. For all orders in a row, it can take from 0.3sec to 1.5sec. This timings are critical for successful and profitable trades.
   
