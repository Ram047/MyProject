import pytest
import sys
import os

sys.path.append(os.path.abspath("src"))

from normalizer import normalize_year, normalize_ticker

# ---------- Year Tests ----------

def test_year_string():
    assert normalize_year("2024") == 2024

def test_year_integer():
    assert normalize_year(2023) == 2023

def test_year_spaces():
    assert normalize_year(" 2022 ") == 2022

def test_year_1999():
    assert normalize_year("1999") == 1999

def test_year_2050():
    assert normalize_year("2050") == 2050

def test_year_none():
    assert normalize_year(None) is None

@pytest.mark.parametrize("value", [
    "",
    "20",
    "abcd",
    "20245",
    "20a4",
    "12-34",
])
def test_invalid_year(value):
    with pytest.raises(ValueError):
        normalize_year(value)


# ---------- Ticker Tests ----------

@pytest.mark.parametrize("ticker,expected", [
    ("aapl", "AAPL"),
    ("AAPL", "AAPL"),
    (" aapl ", "AAPL"),
    ("msft", "MSFT"),
    ("goog", "GOOG"),
    ("tsla", "TSLA"),
    ("amzn", "AMZN"),
    ("meta", "META"),
    ("nflx", "NFLX"),
    ("ibm", "IBM"),
    ("orcl", "ORCL"),
    ("adbe", "ADBE"),
    ("intc", "INTC"),
    ("amd", "AMD"),
    ("nvda", "NVDA"),
    ("shop", "SHOP"),
    ("crm", "CRM"),
    ("uber", "UBER"),
    ("snap", "SNAP"),
    ("sony", "SONY"),
    ("baba", "BABA"),
    ("tcs", "TCS"),
    ("infy", "INFY"),
    ("wipro", "WIPRO"),
    ("hcl", "HCL"),
    ("ltim", "LTIM"),
    ("reliance", "RELIANCE"),
    ("sbin", "SBIN"),
    ("icici", "ICICI"),
])
def test_tickers(ticker, expected):
    assert normalize_ticker(ticker) == expected