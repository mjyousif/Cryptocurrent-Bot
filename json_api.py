import requests

#Stuff to deal with multiple coins
class coinClass:
    def __init__(self, coinQuery, currency):
        self.coinQuery=coinQuery
        self.currency=currency

def classifyQuery(query):
    acceptedCurrencies=["AUD", "BRL", "CAD", "CHF", "CLP", "CNY", "CZK", "DKK", "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "JPY", "KRW", "MXN", "MYR", "NOK", "NZD", "PHP", "PKR", "PLN", "RUB", "SEK", "SGD", "THB", "TRY", "TWD", "ZAR", "USD"]
    querySplit=query.split(" ")
    if not querySplit[-1].upper() in acceptedCurrencies:
        query+=" usd"
    
    currency=query[-3:].lower()
    query=query.replace(", ",",")
    coinList=query[:-4].replace(" ","-")
    coinList=coinList.split(",")
    classifiedQuery=coinClass(coinList,currency)
    return classifiedQuery
#------------------------------------------------------------------
#comma separated numbers that are entered as strings
#keeps precision of the numbers as shown in the coinmarketcap api in usd
def prettyANDprecise(strNum):
    numStrSplit=(strNum.split('.',1))
    numStrFormatLeft="{:,}".format(float(numStrSplit[0]))
    numStrFormatLeft=(numStrFormatLeft.split('.',1))
    if (len(numStrSplit)==1):
        pApOutput=numStrFormatLeft[0]
    else:
        pApOutput=(str(numStrFormatLeft[0])+'.'+numStrSplit[1])
    return pApOutput
    
    
    
def jsonSearch(url, targetSymbol):
    json_data=requests.get(url).json()
    index=0
    for index in range(len(json_data)): #loops through entire coinmarketcap ticker until symbol found
        print (index)
        if targetSymbol.upper()==json_data[index]["symbol"]:
            json_data_end=json_data[index]
            return json_data_end    
    
#-------------------------------------------------------------------
#Function to get the json for the coin
def getCoinData(coin, currency):
    currency=currency.lower()
    if (coin=="" or coin==" "):
        return

    from coinmarketcap import Market
    coinmarketcap=Market()
    json_data_end=coinmarketcap.ticker(limit=0,convert=currency.upper())
    query=coin
    id=query.lower()
    symbol=query.upper()
    for index in range(0,len(json_data_end)):
        # print(index)
        if symbol == json_data_end[index]['symbol'] or id==json_data_end[index]['id']:
            json_data_end=json_data_end[index]
            break
        
    #the result will depend on whether the input was name or symbol
    #The dimensions of the json change depending on that
    #the try-except is to overcome that because that's the first thing i thought of
    try:
        json_data_end=json_data_end[0]
    except:
        json_data_end=json_data_end
        
    #this gets values with comma separations and makes sure that the data exists. if there is null data, replace with "N/A"
    currentPrice='price_'+currency
    currentMarketCap='market_cap_'+currency
    currentVolume='24h_volume_'+currency
    
    if (json_data_end[currentPrice]==None):
        json_data_end[currentPrice]='N/A'
    else:
        json_data_end[currentPrice]=prettyANDprecise(json_data_end[currentPrice])
        if (currentPrice!='price_usd'): #set precision to that of the price_usd
            USDdivide=json_data_end['price_usd'].split(".")
            precision=len(USDdivide[1])
            currencyDivide=json_data_end[currentPrice].split(".")
            json_data_end[currentPrice]=currencyDivide[0]+'.'+currencyDivide[1][0:precision]
    
    if (json_data_end[currentMarketCap]==None):
        json_data_end[currentMarketCap]='N/A'
    else:
        json_data_end[currentMarketCap]=prettyANDprecise(json_data_end[currentMarketCap])
    
    #coinmarketcap info has a decimal at the end of market cap for some reason. this gets rid of that
    json_data_end['market_cap_usd']=json_data_end['market_cap_usd'].split('.')
    json_data_end['market_cap_usd']=json_data_end['market_cap_usd'][0]
                
    if (json_data_end[currentVolume]==None):
        json_data_end[currentVolume]='N/A'
    else:        
        json_data_end[currentVolume]=prettyANDprecise(json_data_end[currentVolume])
    
    if(json_data_end['percent_change_1h']==None):
        json_data_end['percent_change_1h']='?'
    if(json_data_end['percent_change_24h']==None):
        json_data_end['percent_change_24h']='?'
    if(json_data_end['percent_change_7d']==None):
        json_data_end['percent_change_7d']='?'
    
    return json_data_end
    
#----------------------------------------------------------------------

#---------------------------------------------------

    