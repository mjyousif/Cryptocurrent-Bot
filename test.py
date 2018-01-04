# print('x1')
from json_api import *
# print('x2')
query='kekcoin'
# print('x3')
classify=classifyQuery(query)
# print(classify.coinQuery[0]+"|||"+classify.currency)
# print('x4')

print(getCoinData(query,'usd'))

# from coinmarketcap import Market
# coinmarketcap=Market()
# json_data_end=coinmarketcap.ticker(limit=0,convert='USD')
# query='kekcoin'
# id=query.lower()
# symbol=query.upper()
# for index in range(0,len(json_data_end)):
    # # print(index)
    # if symbol == json_data_end[index]['symbol'] or id==json_data_end[index]['id']:
        # print('MEOWMEOWMOEW')
        # json_data_end=json_data_end[index]
        # break
# print(json_data_end)
        
# print(type(json_data_end))
        
        
        
        
# import requests
# url='https://api.coinmarketcap.com/v1/ticker/?limit=0&convert=usd'
# json_data_end=requests.get(url).json()
# print(json_data_end)