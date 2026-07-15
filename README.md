# Nifty 100 Analytics Dashboard

## Overview

Nifty 100 Analytics is a Streamlit-based financial analytics dashboard developed to analyze companies in the Nifty 100 index. The application provides interactive visualizations, stock screening, peer comparison, valuation analysis, trend analysis, sector insights, capital allocation patterns, and access to annual reports using financial data stored in a SQLite database.

---

# Project Structure

```
MyProject/
│
├── database/
│   └── stock_analysis.db
│
├── data/
│   ├── companies.xlsx
│   ├── balancesheet.xlsx
│   ├── cashflow.xlsx
│   ├── market_cap.xlsx
│   ├── profitandloss.xlsx
│   ├── sectors.xlsx
│   ├── peer_groups.xlsx
│   ├── documents.xlsx
│   └── ...
│
├── output/
│   ├── screener_output.xlsx
│   ├── peer_comparison.xlsx
│   ├── valuation_summary.xlsx
│   ├── valuation_flags.csv
│   ├── capital_allocation.csv
│   └── sprint4_retrospective.md
│
├── reports/
│   └── radar_charts/
│
├── src/
│   ├── analytics/
│   ├── dashboard/
│   ├── screener/
│   └── ...
│
└── README.md
```

---

# Features

- Company Financial Profile
- Interactive Stock Screener
- Peer Group Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation Visualization
- Valuation Analytics
- Annual Report Viewer
- Interactive Plotly Charts
- SQLite Database Integration

---

# Requirements

- Python 3.12+
- Streamlit
- Pandas
- Plotly
- OpenPyXL
- SQLite3

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Run Dashboard

Open Command Prompt inside the project folder and run:

```bash
streamlit run src/dashboard/app.py
```

The dashboard will open in your default web browser.

---

# Dashboard Screens

## 1. Home Dashboard

Displays:

- Average ROE
- Median P/E
- Median Debt to Equity
- Total Companies
- Revenue CAGR
- Debt-Free Companies
- Sector Distribution
- Top Companies by Composite Quality Score

---

## 2. Company Profile

Provides:

- Company Search
- Company Information
- Financial KPIs
- Revenue & Net Profit Charts
- ROE & ROCE Trends
- Pros & Cons
- Historical Financial Performance

---

## 3. Stock Screener

Features:

- Interactive Financial Filters
- Six Preset Screeners
- Live Filtering
- CSV Export
- Composite Score Ranking

---

## 4. Peer Comparison

Displays:

- Peer Group Selection
- Radar Chart
- KPI Comparison Table
- Benchmark Company Highlight
- Peer Average Metrics

---

## 5. Trend Analysis

Provides:

- Company Search
- Multi-Metric Selection
- Historical Trend Visualization
- Year-over-Year Growth Annotation
- Financial Data Table

---

## 6. Sector Analysis

Includes:

- Sector Selection
- Interactive Bubble Chart
- Sector Median KPI Comparison
- Company Distribution

---

## 7. Capital Allocation

Displays:

- Capital Allocation Treemap
- Allocation Pattern Selection
- Company List by Allocation Pattern

---

## 8. Annual Reports

Provides:

- Company Search
- Annual Report Years
- Direct BSE PDF Links
- Report Availability Status

---

# Dashboard Outputs

The application generates the following reports:

- screener_output.xlsx
- peer_comparison.xlsx
- valuation_summary.xlsx
- valuation_flags.csv
- capital_allocation.csv
- validation_failures.csv
- sprint4_retrospective.md

---

# Analytics Modules

The project includes:

- Financial Ratio Analysis
- CAGR Analysis
- Cash Flow Analytics
- Stock Screener Engine
- Composite Quality Score
- Peer Percentile Rankings
- Valuation Analytics
- Capital Allocation Analysis

---

# Technologies Used

- Python
- Streamlit
- SQLite
- Pandas
- Plotly
- OpenPyXL
- NumPy

---

# Performance

- Cached database queries using Streamlit Cache
- Responsive interactive dashboard
- Optimized SQLite queries
- Company Profile loads in under 3 seconds
- Interactive Plotly visualizations

---

# Future Improvements

- Live NSE/BSE Market Data Integration
- Portfolio Tracking
- User Authentication
- AI-based Stock Recommendations
- Advanced Financial Forecasting

---

# Author

**Aitha Ramakrishna**

Computer Science & Engineering

Nifty 100 Analytics Dashboard Project

---

# License

This project is developed for educational and analytical purposes.