CREATE TABLE IF NOT EXISTS financial_ratios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,

    net_profit_margin_pct REAL,
    operating_profit_margin_pct REAL,
    return_on_equity_pct REAL,

    debt_to_equity REAL,
    interest_coverage REAL,
    asset_turnover REAL,

    free_cash_flow_cr REAL,
    capex_cr REAL,

    earnings_per_share REAL,
    book_value_per_share REAL,
    dividend_payout_ratio_pct REAL,

    total_debt_cr REAL,
    cash_from_operations_cr REAL,

    revenue_cagr_5yr REAL,
    revenue_cagr_5yr_flag TEXT,

    pat_cagr_5yr REAL,
    pat_cagr_5yr_flag TEXT,

    eps_cagr_5yr REAL,
    eps_cagr_5yr_flag TEXT,

    composite_quality_score REAL,

    UNIQUE(company_id, year)
);