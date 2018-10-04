import requests
import math
import pandas as pd
from datetime import datetime
from datetime import timedelta

import requests
interval = 1
symbol = 'XBTUSD'
# get data from
timestamp_from = 1514761200
# till
timestamp_now = 1536530400


max_back_time = 0
max_bars = 10080
max_bars_time = ((interval * 60) * max_bars)
time_to_iterate = timestamp_now - timestamp_from

baseURI = "https://www.bitmex.com/api/v1"
endpoint = "/trade/bucketed"
time_ago = datetime.now() - timedelta(minutes=150)
request = requests.get(baseURI + endpoint, params={'binSize': '1m', 'symbol': 'XBTUSD', 'count': 750, 'startTime': time_ago})

print("data: start:", datetime.fromtimestamp(timestamp_from), "end:", datetime.fromtimestamp(timestamp_now))

data_frames = []

for x in range(int(math.ceil(time_to_iterate / max_bars_time))):
    if x > 0:
        if (max_back_time - max_bars_time) > timestamp_from:
            max_back_time, timestamp_now = (max_back_time - max_bars_time), max_back_time
        else:
            max_back_time, timestamp_now = timestamp_from, max_back_time

    elif x == 0:
        if time_to_iterate < max_bars_time:
            max_back_time = timestamp_from
        else:
            max_back_time = timestamp_now - max_bars_time

    print("SPLIT TIMING", "start:", datetime.fromtimestamp(max_back_time), "end:", datetime.fromtimestamp(timestamp_now))
    r = requests.get('https://www.bitmex.com/api/udf/history?symbol={}&resolution={}&from={}&to={}'.format(symbol, interval, max_back_time, timestamp_now)).json()

    data = {
        'Date': r['t'],
        'Open': r['o'],
        'High': r['o'],
        'Low': r['o'],
        'Close': r['c'],
        'Adj Close': r['o'],
        'Volume': r['v']
    }

    columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

    df = pd.DataFrame(data, columns=columns)
    df['Date'] = pd.to_datetime(df['Date'], unit='s')
    data_frames.append(df)

print(pd.concat(data_frames))
