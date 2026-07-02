from src.analytics.cashflow import *


def test_free_cash_flow():
    assert free_cash_flow(100, -40) == 60


def test_negative_fcf():
    assert free_cash_flow(100, -150) == -50


def test_cfo_quality_high():
    score, label = cfo_quality_score(120, 100)
    assert label == "High Quality"


def test_cfo_quality_none():
    assert cfo_quality_score(100, 0) is None


def test_capex():
    value, label = capex_intensity(-50, 1000)
    assert label == "Moderate"


def test_fcf_conversion():
    assert fcf_conversion_rate(200, 400) == 50.0


def test_reinvestor():
    assert capital_allocation_pattern(100, -50, -20) == "Reinvestor"


def test_shareholder_returns():
    assert capital_allocation_pattern(100, -50, -20, 1.2) == "Shareholder Returns"


def test_distress():
    assert capital_allocation_pattern(-100, 50, 30) == "Distress Signal"


def test_growth_debt():
    assert capital_allocation_pattern(-50, -40, 100) == "Growth Funded by Debt"