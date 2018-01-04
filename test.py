from json_api import *
query="bitcoin"
classified=classifyQuery(query)
print(classified.coinQuery,"|||",classified.currency)
print(getCoinData(classified.coinQuery[0],classified.currency))
# print(getCoinData('bitcoin-cash','eur'))
# from coinmarketcap import Market
# coinmarketcap=Market()
# json_data_end=coinmarketcap.ticker(limit=0,convert='eur')
# print(json_data_end)z