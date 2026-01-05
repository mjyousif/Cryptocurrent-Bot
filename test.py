import requests
from json_api import *

# sandbox-api.coinmarketcap.com

# x=requests.get('https://api.coinmarketcap.com/v2/ticker/1/?convert=USD').json()
# print('{:f}'.format(x['data']['quotes']['USD']['price']))
# print(1)
# print(.1)
# print(.01)
# print(.001)
# print(.0001)
# print(.00009)
# print(.000001)


def main():

    # alpha=requests.get('https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/map', headers={'X-CMC_PRO_API_KEY':'[CENSORED]'})
    # print (alpha.json()['data'][0])
    # coinInfo=requests.get('https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest', params={'id':str(1),'convert':'GBP'},headers={'X-CMC_PRO_API_KEY':'[CENSORED]'})
    # coinInfo=coinInfo.json()['data']['1']
    # print (coinInfo)

    # sortTypeDict={"name":"name","price":"price","mktcap":"market_cap","1h":"percent_change_1h","1d":"percent_change_24h","7d":"percent_change_7d"}
    # print(sortTypeDict["name"])
    delta = classifyQuery("top")
    print(delta[0].id)


if __name__ == "__main__":
    main()
