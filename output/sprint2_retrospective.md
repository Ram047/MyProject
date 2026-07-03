# Sprint 2 Retrospective

## Sprint Goal

The objective of Sprint 2 was to build a financial ratio engine capable of computing profitability, leverage, efficiency, growth, and cash-flow KPIs across all available company-year records.

## Completed Work

- Implemented profitability ratios: NPM, OPM, ROE, ROCE, and ROA.
- Implemented leverage and efficiency ratios: D/E, ICR, Net Debt, and Asset Turnover.
- Implemented CAGR engine with explicit edge-case flags.
- Implemented cash-flow KPIs and capital-allocation pattern classification.
- Populated the financial_ratios table with 1,164 unique company-year records.
- Completed manual ROE and 5-year Revenue CAGR validation for 3 companies.
- Implemented Financials-sector leverage carve-out.
- Reviewed and categorized ratio anomalies.

## Formula Decisions

1. Net Profit Margin returns None when sales is zero.
2. ROE returns None when equity plus reserves is zero or negative.
3. Debt-to-Equity returns 0 for debt-free companies.
4. Interest Coverage returns None when interest is zero and is labelled Debt Free.
5. Financials-sector companies are exempt from the standard high D/E warning.
6. CAGR calculations return explicit flags for turnaround, decline-to-loss, both-negative, zero-base, and insufficient-history cases.
7. Negative Free Cash Flow values are retained because they can represent genuine capital investment.
8. Ratio-engine ROE values are used for analytics; source ROE values are retained for display/reference.

## Edge Case Review

The source dataset contains 23 companies classified under the Financials broad sector, while the sprint specification referenced 19. The implementation follows the loaded source taxonomy and applies the leverage carve-out dynamically to all 23 Financials companies.

The ratio edge-case review identified 59 anomalies:
- 30 version differences
- 28 formula discrepancies
- 1 data source issue

The TCS source ROE value of 0.52 was identified as anomalous compared with the ratio-engine ROE of 45.42. The computed value is used for analytics.

## Data Modeling Observation

Multiple reporting periods can normalize to the same calendar year, such as Mar 2024 and Sep 2024. The current engine resolves these using the latest record after normalization. A future production version should retain full reporting-period dates to avoid calendar-year granularity loss.

## Sprint Outcome

Sprint 2 successfully produced a populated financial ratio analytics layer with automated KPI calculations, explicit edge-case handling, anomaly logging, and manual validation evidence.