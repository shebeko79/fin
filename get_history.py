import requests
import pickle
from requests.structures import CaseInsensitiveDict
import time
import datetime
import os.path

def request_arr(time_unix):
    url = "https://api.binance.com/api/v3/klines?limit=1000&symbol=BTCUSDT&interval=1m&startTime="+str(time_unix)
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    resp = requests.get(url, headers=headers)
    return resp.json()


from_time = datetime.datetime(2021, 7, 17, 0, 0)
from_time_unix = int(datetime.datetime.timestamp(from_time)*1000)

arr = []
if os.path.exists('history.dat'):
    f = open('history.dat', 'rb')
    arr = pickle.load(f)

time_unix = from_time_unix
if len(arr) > 0:
    time_unix = arr[-1][0] + 1

i = 0
while True:
    arr_ret = request_arr(time_unix)
    time_unix = arr_ret[-1][0]+1

    date_time = datetime.datetime.fromtimestamp(time_unix/1000)
    print("i=", i, "date=", date_time.strftime('%Y-%m-%d %H:%M:%S'))

    arr += arr_ret

    if len(arr_ret) < 1000:
        break

    if i % 40 == 0:
        print("saving...")
        f = open('history.dat', 'wb')
        pickle.dump(arr, f)
    i += 1

f = open('history.dat', 'wb')
pickle.dump(arr, f)

