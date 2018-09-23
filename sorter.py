# from json_api import *
# query='ethereum, bitcoin cash, btc, litecoin, ripple, iota, monero, nano'
# a=classifyQuery(query)
# print('---------------------------------')
# for i in range(0, len(a.coinQuery)):
    # print(a.jsonList[i]['price_'+a.currency])
# print('---------------------------------')
# a.jsonList.sort(key=lambda x:float(x['price_'+a.currency].replace(',','')), reverse = True)
# for i in range(0, len(a.coinQuery)):
    # print(a.jsonList[i]['price_'+a.currency])
# print('---------------------------------')
# a.jsonList.sort(key=lambda x:x['name'], reverse = False)
# for i in range(0, len(a.coinQuery)):
    # print(a.jsonList[i]['name'])
    
def valueSorter(cryptoList, sortKey):
    if sortKey=="":
        return cryptoList
    elif sortKey=="alpha":
        cryptoList.sort(key=lambda x:x.name, reverse = False)
        return cryptoList
    elif sortKey=="price":
        cryptoList.sort(key=lambda x:float(x.price.replace(',','')), reverse = True)
        return cryptoList        
    elif sortKey=="mktcap":
        cryptoList.sort(key=lambda x:float(x.market_cap.replace(',','')), reverse = True)
        return cryptoList        
    elif sortKey=="1h":
        cryptoList.sort(key=lambda x:float(x.percent_change_1h), reverse = True)
        return cryptoList        
    elif sortKey=="1d":
        cryptoList.sort(key=lambda x:float(x.percent_change_24h), reverse = True)
        return cryptoList    
    elif sortKey=="7d":
        cryptoList.sort(key=lambda x:float(x.percent_change_7d), reverse = True)
        return cryptoList   