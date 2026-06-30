import pytest

from src.analytics.ratios import (
    # Day 08
    net_profit_margin,
    operating_profit_margin,
    opm_cross_check,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,

    # Day 09
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_label,
    icr_warning_flag,
    net_debt,
    asset_turnover,
)


# ==========================
# Day 08 Tests
# ==========================

def test_net_profit_margin():
    assert net_profit_margin(200, 1000) == 20.0


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(100, 0) is None


def test_operating_profit_margin():
    assert operating_profit_margin(250, 1000) == 25.0


def test_opm_cross_check_match():
    assert opm_cross_check(25.0, 25.5) is True


def test_opm_cross_check_mismatch():
    assert opm_cross_check(25.0, 27.5) is False


def test_return_on_equity():
    assert return_on_equity(150, 500, 500) == 15.0


def test_return_on_equity_negative():
    assert return_on_equity(100, -200, 100) is None


def test_return_on_capital_employed():
    assert return_on_capital_employed(200, 500, 500, 1000) == 10.0


def test_return_on_assets():
    assert return_on_assets(100, 1000) == 10.0


def test_return_on_assets_zero():
    assert return_on_assets(100, 0) is None


# ==========================
# Day 09 Tests
# ==========================

def test_debt_to_equity():
    assert debt_to_equity(500, 250, 250) == 1.0


def test_debt_free():
    assert debt_to_equity(0, 500, 500) == 0


def test_high_leverage():
    assert high_leverage_flag(6.0, "Industrials") is True


def test_financial_sector_not_flagged():
    assert high_leverage_flag(6.0, "Financials") is False


def test_interest_coverage():
    assert interest_coverage_ratio(200, 50, 50) == 5.0


def test_interest_zero():
    assert interest_coverage_ratio(200, 50, 0) is None


def test_icr_label():
    assert icr_label(None) == "Debt Free"


def test_icr_warning():
    assert icr_warning_flag(1.2) is True


def test_net_debt():
    assert net_debt(500, 200) == 300


def test_asset_turnover():
    assert asset_turnover(1000, 500) == 2.0


def test_asset_turnover_zero():
    assert asset_turnover(1000, 0) is None