import sys
import websocket
import json
import time
import datetime
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.helpers import round_step_size
import logging

history_arr = []

buyRatio = 18300 / 19000
flatRatio = 18700 / 18300
spotName='BTCUSDT'

SEARCH_BUY = 1
SEARCH_SELL = 2

sellRatio = 18050 / 18000
stopLossRatio = 17500 / 18000
sellMinutesTimeout = 2 * 60

last_time_oco = 0
last_buy_time = 0
last_buy_price = 0

state = SEARCH_BUY

stableDelay = 1 * 60
tick_size = 0.00001
tick_money_size = 0.01

sellPrice = 0
lossPrice = 0

client = []

def do_connect():
    global client
    client = Client('15IBBSRYUuEg0Yzrm6nErZ8qOehsVgn2VVPzYUInNehz4OntA3FZAOxoVeaiAn9h','gIn2I2j49iepVoBPtiA6GrcEUivresoaebNJUFvOvcB2h2Sv28l1Aqh9ajxlVC5Y')

do_connect()


orders = client.get_open_orders(symbol='BTCUSDT')
if len(orders) != 0:
    raise SystemExit('Cancel your open orders first. Then run script again.')

btc = 0
money = 0

def getAssetAmmount():
    global btc
    global money
    btc = float(client.get_asset_balance(asset='BTC')['free'])
    money = float(client.get_asset_balance(asset='USDT')['free'])

getAssetAmmount()
print(f'btc={btc} money={money}')

if money < 50:
    raise SystemExit('You need at least 50USDT to run')


#order = client.order_market_buy(
#    symbol=spotName,
#    quoteOrderQty=75)

#{'symbol': 'BTCUSDT', 'orderId': 13336938452, 'orderListId': -1, 'clientOrderId': 'H7SaNdyV73X607XTIlRWvj', 'transactTime': 1662839908528,
# 'price': '0.00000000', 'origQty': '0.00347000', 'executedQty': '0.00347000', 'cummulativeQuoteQty': '74.86493770', 'status': 'FILLED',
# 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY',
# 'fills': [
# {'price': '21574.91000000', 'qty': '0.00100000', 'commission': '0.00000000', 'commissionAsset': 'BNB', 'tradeId': 1790238507},
# {'price': '21574.91000000', 'qty': '0.00247000', 'commission': '0.00000000', 'commissionAsset': 'BNB', 'tradeId': 1790238508}]}                                        btc=0.00353193 money=0.1795919

#21574.91
#order = client.order_oco_sell(
#    symbol = spotName,
#    quantity = round_step_size(btc, tick_size),
#    price= '21600',
#    stopPrice= '21000',
#    stopLimitPrice= '20000',
#    stopLimitTimeInForce= 'GTC')

#{'orderListId': 74305427, 'contingencyType': 'OCO', 'listStatusType': 'EXEC_STARTED', 'listOrderStatus': 'EXECUTING',
# 'listClientOrderId': 'yGHgU2ORhVFFfviHRZBVJ8', 'transactionTime': 1662841800807, 'symbol': 'BTCUSDT', 'orders':
# [{'symbol': 'BTCUSDT', 'orderId': 13337544801, 'clientOrderId': '7pE4KkijeBHY0zkEcCb7wE'},
# {'symbol': 'BTCUSDT', 'orderId': 13337544802, 'clientOrderId': 'TchQrPgz5zVYt2s0ojD3h9'}],
# 'orderReports': [{'symbol': 'BTCUSDT', 'orderId': 13337544801, 'orderListId': 74305427,
# 'clientOrderId': '7pE4KkijeBHY0zkEcCb7wE', 'transactTime': 1662841800807, 'price': '20000.00000000', 'origQty': '0.00353000',
# 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'STOP_LOSS_LIMIT',
# 'side': 'SELL', 'stopPrice': '21000.00000000'}, {'symbol': 'BTCUSDT', 'orderId': 13337544802, 'orderListId': 74305427,
# 'clientOrderId': 'TchQrPgz5zVYt2s0ojD3h9', 'transactTime': 1662841800807, 'price': '21600.00000000', 'origQty': '0.00353000',
# 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT_MAKER', 'side': 'SELL'}]}

#orders = client.get_open_orders(symbol='BTCUSDT')
#print(orders)
#[
# {'symbol': 'BTCUSDT', 'orderId': 13337544801, 'orderListId': 74305427, 'clientOrderId': '7pE4KkijeBHY0zkEcCb7wE',
# 'price': '20000.00000000', 'origQty': '0.00353000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000',
# 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'STOP_LOSS_LIMIT', 'side': 'SELL', 'stopPrice': '21000.00000000',
# 'icebergQty': '0.00000000', 'time': 1662841800807, 'updateTime': 1662841800807, 'isWorking': False, 'origQuoteOrderQty': '0.00000000'},
# {'symbol': 'BTCUSDT', 'orderId': 13337544802, 'orderListId': 74305427, 'clientOrderId': 'TchQrPgz5zVYt2s0ojD3h9', 'price': '21600.00000000',
# 'origQty': '0.00353000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT_MAKER',
# 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1662841800807, 'updateTime': 1662841800807, 'isWorking': True,
# 'origQuoteOrderQty': '0.00000000'}]

def isTimeToBuy():
    if len(history_arr) < stableDelay:
        return True

    mh = history_arr[-1]
    price = float(mh['c'])

    mh2 = history_arr[-stableDelay]
    price_high = float(mh['h'])

    if price / price_high < buyRatio:
        return False

    return True

def cancelOrders():
    global client
    global spotName

    print('cancelOrders')
    orders = client.get_open_orders(symbol=spotName)
    if len(orders) == 0:
        return False

    o = orders[0]
    id = o['orderId']
    print(f'cancelOrders id={id}')
    client.cancel_order(
        symbol=spotName,
        orderId = id)

    return True

def check_connection():
    global client
    need_reconnect = False
    try:
        client.ping()
    except:
        print('ping failed')
        need_reconnect = True

    if need_reconnect:
        print('trying to reconnect...')
        do_connect()
        print('reconnected')

def process(obj) :

    global history_arr
    global client
    global money
    global btc
    global last_buy_time
    global last_buy_price
    global last_time_oco
    global spotName
    global state
    global sellPrice
    global lossPrice

    price = obj['c']

    if len(history_arr) == 0 or history_arr[-1]['t'] != obj['t']:
        history_arr.append(obj)

        time_str = datetime.datetime.fromtimestamp(obj['t'] / 1000)
        print(f'{time_str} price={price} state={state}')
    else:
        history_arr[-1] = obj

    if len(history_arr) > stableDelay * 2:
        history_arr = history_arr[stableDelay:]

    if state == SEARCH_BUY:
        if isTimeToBuy():
            print(f'time to buy: price={price}')
            check_connection()
            order = client.order_market_buy(
                symbol=spotName,
                quoteOrderQty=round_step_size(money, tick_money_size))

            if order['status'] != 'FILLED':
                raise SystemExit('Buy order not filled')

            last_buy_price = float(order['cummulativeQuoteQty'])/float(order['executedQty'])
            last_buy_time = int(time.time()/60)
            getAssetAmmount()

            print(f'buy on price={last_buy_price} last_buy_time={last_buy_time} btc={btc} money={money}')

            sellPrice = last_buy_price * sellRatio
            lossPrice = last_buy_price * stopLossRatio

            order = client.order_oco_sell(
                symbol=spotName,
                quantity=round_step_size(btc, tick_size),
                price=round_step_size(sellPrice, tick_money_size),
                stopPrice=round_step_size(lossPrice, tick_money_size),
                stopLimitPrice=round_step_size(lossPrice * 0.98, tick_money_size),
                stopLimitTimeInForce='GTC')

            last_time_oco = last_buy_time
            print(f'push oco: sellPrice={sellPrice} lossPrice={lossPrice}')

            state = SEARCH_SELL
    elif state == SEARCH_SELL:
        cur_time = int(time.time() / 60)

        if cur_time >= last_buy_time + sellMinutesTimeout:
            print(f'SELL timeout: cur_price={price}')
            check_connection()
            if cancelOrders():
                getAssetAmmount()

                order = client.order_market_sell(
                    symbol=spotName,
                    quantity = round_step_size(btc, tick_size))

                if order['status'] != 'FILLED':
                    raise SystemExit('Stop loss timeout order not filled')

                price = float(order['cummulativeQuoteQty'])/float(order['executedQty'])

            getAssetAmmount()
            print(f'timeout on price={price} btc={btc} money={money}')
            state = SEARCH_BUY

        elif cur_time >= last_time_oco + sellMinutesTimeout / 10:
            print(f'SELL remake oco: cur_price={price}')
            check_connection()
            dt = 1.0 - (cur_time - last_buy_time) / sellMinutesTimeout
            sellPrice = last_buy_price + (last_buy_price * sellRatio - last_buy_price) * dt
            lossPrice = last_buy_price + (last_buy_price * stopLossRatio - last_buy_price) * dt

            if cancelOrders():
                order = client.order_oco_sell(
                    symbol=spotName,
                    quantity=round_step_size(btc, tick_size),
                    price=round_step_size(sellPrice, tick_money_size),
                    stopPrice=round_step_size(lossPrice, tick_money_size),
                    stopLimitPrice=round_step_size(lossPrice * 0.98, tick_money_size),
                    stopLimitTimeInForce='GTC')

                print(f'repush oco: sellPrice={sellPrice} lossPrice={lossPrice}')
                last_time_oco = cur_time
            else:
                getAssetAmmount()
                print(f'oco executed: btc={btc} money={money}')
                state = SEARCH_BUY
        else:
            high_price = float(obj['h'])
            low_price = float(obj['l'])

            if high_price >= sellPrice or low_price <= lossPrice:
                orders = client.get_open_orders(symbol=spotName)
                print(f'oco must be executed: {high_price}>={sellPrice} or {low_price}<={lossPrice} len(orders) ={len(orders)}')
                if len(orders) == 0:
                    getAssetAmmount()
                    print(f'oco executed: btc={btc} money={money}')
                    state = SEARCH_BUY


def on_message(ws, message):
    try:
        obj = json.loads(message)

        # {'t': 1658047080000, 'T': 1658047139999, 's': 'BTCUSDT', 'i': '1m', 'f': 12227542, 'L': 12227543,
        #    'o': '21389.14000000', 'c': '21392.50000000', 'h': '21392.50000000', 'l': '21389.14000000', 'v': '0.03418000',
        #    'n': 2, 'x': False, 'q': '731.10829000', 'V': '0.03418000', 'Q': '731.10829000', 'B': '0'}
        obj = obj['k']

        process(obj)
    except BaseException as e:
        sys.exit(str(e))


def on_error(ws, error):
    print(error)


def on_close(close_msg):
    print(close_msg)


def streamKline(symbol, interval):
    socket = f'wss://stream.binance.us:9443/ws/{symbol}@kline_{interval}'
    ws = websocket.WebSocketApp(socket,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()


streamKline('btcusdt', '1m')
