import requests
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
	
def queryLength(query):
	queryList=query.split(" ")
	queryLength=len(queryList)
	return queryLength
	
def querySplit(query):
	acceptedCurrencies=["AUD", "BRL", "CAD", "CHF", "CLP", "CNY", "CZK", "DKK", "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "JPY", "KRW", "MXN", "MYR", "NOK", "NZD", "PHP", "PKR", "PLN", "RUB", "SEK", "SGD", "THB", "TRY", "TWD", "ZAR", "USD"]
	
	querySplit=query.split(" ")
	#loop to see if there is a currency, or if needs the default
	i=0
	defaultCurrency=True
	for i in range(len(acceptedCurrencies)):
		if(querySplit[-1].upper()==acceptedCurrencies[i]):
			defaultCurrency=False
	if defaultCurrency==True:
		querySplit.append('usd')
	#the output should always be 2 indices, one for the coin, the other for the currency
	#if there are more than two, then the coin is multiple words
	while(len(querySplit)>2):
		querySplit[0]=querySplit[0]+'-'+querySplit[1]
		del querySplit[1]
		
	#todo, make sure 2nd word is currency| append the currency symbol
	return querySplit
#-------------------------------------------------------------------
#Function to get the json for the coin
def getCoinData(query):
	if (query=="" or query==" "):
		return
	splitQuery=querySplit(query)
	main_api='https://api.coinmarketcap.com/v1/ticker/'
	coin=splitQuery[0].replace(" ","-")
	url=main_api+coin
	url=url+'/?convert='+splitQuery[1]
	json_data_end=requests.get(url).json() 
	if 'error' in json_data_end: #This will check if the entered name exists, if not, check if the symbol exists
		url='https://api.coinmarketcap.com/v1/ticker/?limit=10000'+'&convert='+splitQuery[1]
		json_data=requests.get(url).json()
		index=0
		for index in range(len(json_data)): #loops through entire coinmarketcap ticker until symbol found
			if coin.upper()==json_data[index]["symbol"]:
				json_data_end=json_data[index]
				break	

	#the result will depend on whether the input was name or symbol
	#The dimensions of the json change depending on that
	#the try-except is to overcome that because that's the first thing i thought of
	try:
		json_data_end=json_data_end[0]
	except:
		json_data_end=json_data_end
		
	#this gets values with comma separations and makes sure that the data exists. if there is null data, replace with "N/A"
	currentPrice='price_'+splitQuery[1]
	currentMarketCap='market_cap_'+splitQuery[1]
	currentVolume='24h_volume_'+splitQuery[1]
	
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

#Function to get market cap
def cryptoMarketCap(querySplit, coinData):
	# name=coinData['name']
	marketCap=coinData['market_cap_'+querySplit[1]]	
	marketCapOutput=marketCap+' '+querySplit[1].upper()
	return marketCapOutput

	#Function to get crypto value
def cryptoValueMain(querySplit, coinData):
	# name=coinData['name']
	price=coinData['price_'+querySplit[1]]		
	valueOutput=price+' '+querySplit[1].upper()
	return valueOutput

	#function gets percent change in 1 hour
def oneHourChange(coinData):
	# name=coinData['name']
	pctChange1hr=coinData['percent_change_1h']
	oneHourChangeOutput="1 hour percent change: "+pctChange1hr+"%"
	return oneHourChangeOutput

	#function gets percent change in 24 hour
def oneDayChange(coinData):
	# name=coinData['name']
    # priceUSD=coinData['price_usd']	
    pctChange24hr=coinData['percent_change_24h']
    oneDayChangeOutput="24 hour percent change: "+pctChange24hr+"%"
    return oneDayChangeOutput

	#function gets percent change in 7 days
def sevenDayChange(coinData):
	# name=coinData['name']	
	pctChange7d=coinData['percent_change_7d']
	sevenDayChangeOutput="7 day percent change: "+pctChange7d+"%"
	return sevenDayChangeOutput
	
	#function presents all all the above data in one string
def summary(querySplit, coinData):
	name=coinData['name']
	marketCap=cryptoMarketCap(querySplit,coinData)
	price=cryptoValueMain(querySplit,coinData)
	pctChange1hr=coinData['percent_change_1h']
	pctChange24hr=coinData['percent_change_24h']
	pctChange7d=coinData['percent_change_7d']
	summaryOutput=("---"+name+" Summary---"+
		"\nPrice: "+price+
		"\nMarket Capitalization: "+marketCap+
		"\n1 hour percent change: "+pctChange1hr+"%"+
		"\n24 hour percent change: "+pctChange24hr+"%"+
		"\n7 day percent change: "+pctChange7d+"%")
	return summaryOutput
#---------------------------------------------------

	