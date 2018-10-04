import datetime
import requests
from pprint import pprint
baseURI = "https://www.bitmex.com/api/v1"
endpoint = "/trade/bucketed"
time_ago = datetime.datetime.now() - datetime.timedelta(minutes=150)
request = requests.get(baseURI + endpoint, params={'binSize': '1m', 'symbol': 'XBTUSD', 'count': 750, 'startTime': time_ago})
pprint(request.json())