import pytest
from services.sorter import valueSorter

class MockCrypto:
    def __init__(self, name, price, market_cap, pc_1h, pc_24h, pc_7d):
        self.name = name
        self.price = str(price)
        self.market_cap = str(market_cap)
        self.percent_change_1h = str(pc_1h)
        self.percent_change_24h = str(pc_24h)
        self.percent_change_7d = str(pc_7d)

def test_value_sorter_empty_key():
    crypto_list = [MockCrypto("A", 10, 100, 1, 1, 1)]
    assert valueSorter(crypto_list, "") == crypto_list

def test_value_sorter_alpha():
    c1 = MockCrypto("Zeta", 10, 100, 1, 1, 1)
    c2 = MockCrypto("Alpha", 20, 200, 2, 2, 2)
    crypto_list = [c1, c2]
    
    sorted_list = valueSorter(crypto_list, "alpha")
    assert sorted_list[0].name == "Alpha"
    assert sorted_list[1].name == "Zeta"

def test_value_sorter_price():
    c1 = MockCrypto("A", "10,000", 100, 1, 1, 1) # Testing comma replacement
    c2 = MockCrypto("B", "20,000", 200, 2, 2, 2)
    crypto_list = [c1, c2]
    
    sorted_list = valueSorter(crypto_list, "price")
    assert sorted_list[0].name == "B" # Descending
    assert sorted_list[1].name == "A"

def test_value_sorter_mktcap():
    c1 = MockCrypto("A", 10, "1,000,000", 1, 1, 1)
    c2 = MockCrypto("B", 20, "500,000", 2, 2, 2)
    crypto_list = [c1, c2]
    
    sorted_list = valueSorter(crypto_list, "mktcap")
    assert sorted_list[0].name == "A" # Descending
    assert sorted_list[1].name == "B"

def test_value_sorter_1h():
    c1 = MockCrypto("A", 10, 100, 1.5, 1, 1)
    c2 = MockCrypto("B", 20, 200, -2.0, 2, 2)
    c3 = MockCrypto("C", 30, 300, 3.5, 3, 3)
    crypto_list = [c1, c2, c3]
    
    sorted_list = valueSorter(crypto_list, "1h")
    assert sorted_list[0].name == "C"
    assert sorted_list[1].name == "A"
    assert sorted_list[2].name == "B"

def test_value_sorter_1d():
    c1 = MockCrypto("A", 10, 100, 1, 10.5, 1)
    c2 = MockCrypto("B", 20, 200, 2, 20.5, 2)
    crypto_list = [c1, c2]
    
    sorted_list = valueSorter(crypto_list, "1d")
    assert sorted_list[0].name == "B"
    assert sorted_list[1].name == "A"

def test_value_sorter_7d():
    c1 = MockCrypto("A", 10, 100, 1, 1, -5.5)
    c2 = MockCrypto("B", 20, 200, 2, 2, 5.5)
    crypto_list = [c1, c2]
    
    sorted_list = valueSorter(crypto_list, "7d")
    assert sorted_list[0].name == "B"
    assert sorted_list[1].name == "A"

def test_value_sorter_invalid_key():
    c1 = MockCrypto("A", 10, 100, 1, 1, 1)
    crypto_list = [c1]
    # Invalid key returns None according to python logic if no default return exists,
    # let's verify what happens in the code. In sorter.py it falls through without returning, so returns None.
    assert valueSorter(crypto_list, "invalid") is None
