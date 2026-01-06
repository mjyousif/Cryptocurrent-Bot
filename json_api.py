"""Legacy compatibility module.

This module preserves a subset of the original `json_api` functions for
backwards compatibility but delegates business logic to the `services` package.
"""

import os
import warnings
from dotenv import load_dotenv
from sorter import *
from services.crypto_service import get_crypto_list

# Load environment variables from .env file
load_dotenv()


# Stuff to deal with multiple coins
class coinClass:
    def __init__(self, coinQuery, currency, jsonList, sortType):
        self.coinQuery = coinQuery
        self.currency = currency
        self.jsonList = jsonList
        self.sortType = sortType


class cryptoClass:
    # NOTE: THE IF STATEMENTS HERE ARE NOT NEEDED ANYMORE
    # CMC DOES NOT HAVE THE N/A BUILT IN, THEY JUST USE 0
    def __init__(self, coinInfo, currency):
        # Will have access to : id,name, symbol, price, market_cap, percent_change_1h, percent_change_24h, percent_change_7d, currency

        self.id = str(coinInfo["id"])
        self.currency = currency
        # Name Check
        if coinInfo["name"] == None:
            self.name = "N/A"
        else:
            self.name = coinInfo["name"]

        # Symbol Check
        if coinInfo["symbol"] == None:
            self.symbol = "N/A"
        else:
            self.symbol = coinInfo["symbol"]

        # Price Check
        if coinInfo["quote"][currency]["price"] == None:
            self.price = "N/A"
        else:
            self.price = self.priceCommaPrecision(coinInfo["quote"][currency]["price"])

        # Market Cap Check
        if coinInfo["quote"][currency]["market_cap"] == None:
            self.market_cap = "N/A"
        else:
            self.market_cap = self.priceCommaPrecision(
                coinInfo["quote"][currency]["market_cap"]
            )
        # 1h check
        if coinInfo["quote"][currency]["percent_change_1h"] == None:
            self.percent_change_1h = "N/A"
        else:
            self.percent_change_1h = str(
                coinInfo["quote"][currency]["percent_change_1h"]
            )

        # 1d check
        if coinInfo["quote"][currency]["percent_change_24h"] == None:
            self.percent_change_24h = "N/A"
        else:
            self.percent_change_24h = str(
                coinInfo["quote"][currency]["percent_change_24h"]
            )

        # 1w check
        if coinInfo["quote"][currency]["percent_change_7d"] == None:
            self.percent_change_7d = "N/A"
        else:
            self.percent_change_7d = str(
                coinInfo["quote"][currency]["percent_change_7d"]
            )

    # Make the price have commas and appropriate decimals
    def priceCommaPrecision(self, price):
        if price == 0:  # unavailable prices are 0, so i will return N/A
            return "N/A"
        priceStr = str(price)  # if the price is available, add commas where desirable
        priceStr = priceStr.split(".")
        if price >= 1.00:
            priceStr[1] = priceStr[1][0:2]
        else:
            priceStr[1] = priceStr[1][0:6]
        priceStr[0] = "{:,}".format(int(priceStr[0]))
        priceStr = ".".join(priceStr)
        return priceStr


# this function is usually called whenever any query is passed
# it will return a list of each crypto with the price, market cap, etc, information in the given currency
def classifyQuery(query):
    """Deprecated compatibility wrapper.

    Delegates to `services.get_crypto_list` and returns its result. Emits a
    DeprecationWarning the first time it's called.
    """
    warnings.warn(
        "json_api.classifyQuery is deprecated; use services.get_crypto_list instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_crypto_list(query)


raise ImportError(
    "The 'json_api' module has been removed. Use 'services' (e.g., services.get_crypto_list) or 'data' modules instead."
)
