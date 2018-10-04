import json
import pandas as pd
from datetime import datetime

df = pd.DataFrame(json.loads(open('prices.json').read()), columns=['o', 'c', 'v'])
print(df.head(20))
# print(df.resample('10min').T)
# for item in data.keys():
#     print(datetime.fromtimestamp(int(item)))