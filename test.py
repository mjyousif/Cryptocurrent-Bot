# from json_api import *
# import decimal
# x=getCoinData('btc')
# print(float(x['price_usd']))
# print(oneHourChange('doge'))
# string="123.4567"
# print (string)
# y=(string.split('.',1))
# print (len(y[1]))
# print ("%f" % 1.2399)


#-------------------------------------------------
from json_api import *
# # numStr='2181.120'
# # numStrSplit=(numStr.split('.',1))
# # numStrFormatLeft="{:,}".format(float(numStrSplit[0]))
# # numStrFormatLeft=(numStrFormatLeft.split('.',1))
# # numStrFormat=(str(numStrFormatLeft[0])+'.'+numStrSplit[1])
# # print (numStrFormat)
# print(prettyANDprecise('2183.1200'))
#------------------------------
# print(getCoinData('ltc'))
# print(prettyANDprecise('2183'))
# print('------')
# print(prettyANDprecise('2183.120'))
print(getCoinData('bitcoin'))
print(getCoinData('ltc'))
print(getCoinData('ponzi'))