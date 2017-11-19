import requests

#-------------------------------------------------------------------
#Function to get the json for the coin
def getCoinData(coin):
	main_api='https://api.coinmarketcap.com/v1/ticker/'
	coin=coin.replace(" ","-")
	url=main_api+coin
	json_data_end=requests.get(url).json() 
	if 'error' in json_data_end: #This will check if the entered coin exists, if not, check if the symbol exists
		url=main_api
		json_data=requests.get(url).json()
		index=0
		for index in range(len(json_data)): #loops through entire coinmarketcap ticker until symbol found
			if coin.upper()==json_data[index]["symbol"]:
				json_data_end=json_data[index]
				index==len(json_data)	
#	print (output)
	try:
		json_data_end=json_data_end[0]
	except:
		json_data_end=json_data_end
	return json_data_end
	#the result will depend on whether the input was name or symbol
	#the try-except is to overcome that because that's the first thing i thought of
#----------------------------------------------------------------------

#Function to get market cap
def cryptoMarketCap(coin):
	coinData=getCoinData(coin)
	name=coinData['name']
	marketCap=coinData['market_cap_usd']	
	marketCapOutput=(name+' market capitalization: $'+marketCap)
	return marketCapOutput

	#Function to get crypto value
def cryptoValueMain(coin):
	coinData=getCoinData(coin)
	name=coinData['name']
	priceUSD=coinData['price_usd']		
	valueOutput=(name+': $'+priceUSD)
	return valueOutput
	
def oneHourChange(coin):
	coinData=getCoinData(coin)
	name=coinData['name']
	priceUSD=coinData['price_usd']	
	pctChange1hr=coinData['percent_change_1h']
#	dollarChange1hr=float(priceUSD)/(1+float(pctChange1hr)/100)
	oneHourChangeOutput=(name+" 1 hour percent change: "+pctChange1hr+"%")
	return oneHourChangeOutput

def oneDayChange(coin):
	coinData=getCoinData(coin)
	name=coinData['name']
	priceUSD=coinData['price_usd']	
	pctChange24hr=coinData['percent_change_24h']
	oneDayChangeOutput=(name+" 24 hour percent change: "+pctChange24hr+"%")	
	return oneDayChangeOutput

def sevenDayChange(coin):
	coinData=getCoinData(coin)
	name=coinData['name']
	priceUSD=coinData['price_usd']	
	pctChange7d=coinData['percent_change_7d']
	sevenDayChangeOutput=(name+" 7 day percent change: "+pctChange7d+"%")		
	return sevenDayChangeOutput
	
def summary(coin):
	coinData=getCoinData(coin)
	name=coinData['name']
	marketCap=coinData['market_cap_usd']
	priceUSD=coinData['price_usd']	
	pctChange1hr=coinData['percent_change_1h']
	pctChange24hr=coinData['percent_change_24h']
	pctChange7d=coinData['percent_change_7d']
	summaryOutput=("---"+name+" Summary---"+
		"\nPrice USD: $"+priceUSD+
		"\nMarket Capitalization: $"+marketCap+
		"\n1 hour percent change: "+pctChange1hr+"%"+
		"\n24 hour percent change: "+pctChange24hr+"%"+
		"\n7 day percent change: "+pctChange7d+"%")
	return summaryOutput