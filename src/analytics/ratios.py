# ==========================
# Day 08 - Profitability Ratios
# ==========================

def net_profit_margin(net_profit, sales):
    """
    Net Profit Margin = (Net Profit / Sales) * 100
    """
    if sales == 0:
        return None
    return round((net_profit / sales) * 100, 2)


def operating_profit_margin(operating_profit, sales):
    """
    Operating Profit Margin = (Operating Profit / Sales) * 100
    """
    if sales == 0:
        return None
    return round((operating_profit / sales) * 100, 2)


def opm_cross_check(calculated_opm, stored_opm):
    """
    Returns True if difference <= 1%
    """
    if calculated_opm is None or stored_opm is None:
        return True
    return abs(calculated_opm - stored_opm) <= 1


def return_on_equity(net_profit, equity_capital, reserves):
    """
    ROE = Net Profit / (Equity + Reserves) * 100
    """
    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round((net_profit / equity) * 100, 2)


def return_on_capital_employed(ebit, equity_capital, reserves, borrowings):
    """
    ROCE = EBIT / (Equity + Reserves + Borrowings) * 100
    """
    capital = equity_capital + reserves + borrowings

    if capital <= 0:
        return None

    return round((ebit / capital) * 100, 2)


def return_on_assets(net_profit, total_assets):
    """
    ROA = Net Profit / Total Assets * 100
    """
    if total_assets == 0:
        return None

    return round((net_profit / total_assets) * 100, 2)


# ==========================
# Day 09 - Leverage & Efficiency Ratios
# ==========================

def debt_to_equity(borrowings, equity_capital, reserves):
    """
    Debt-to-Equity = Borrowings / (Equity + Reserves)
    """
    if borrowings == 0:
        return 0

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round(borrowings / equity, 2)


def high_leverage_flag(de_ratio, broad_sector):
    """
    High leverage if D/E > 5 and company is not in Financials.
    """
    if de_ratio is None:
        return False

    return de_ratio > 5 and broad_sector != "Financials"


def interest_coverage_ratio(operating_profit, other_income, interest):
    """
    ICR = (Operating Profit + Other Income) / Interest
    """
    if interest == 0:
        return None

    return round((operating_profit + other_income) / interest, 2)


def icr_label(icr):
    """
    Returns 'Debt Free' if interest is zero (ICR is None)
    """
    if icr is None:
        return "Debt Free"
    return ""


def icr_warning_flag(icr):
    """
    Warning if ICR < 1.5
    """
    if icr is None:
        return False

    return icr < 1.5


def net_debt(borrowings, investments):
    """
    Net Debt = Borrowings - Investments
    """
    return borrowings - investments


def asset_turnover(sales, total_assets):
    """
    Asset Turnover = Sales / Total Assets
    """
    if total_assets == 0:
        return None

    return round(sales / total_assets, 2)