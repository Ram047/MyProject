import pytest

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    opm_cross_check,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
)


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