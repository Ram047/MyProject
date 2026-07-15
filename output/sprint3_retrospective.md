# Sprint 3 Retrospective

## Sprint Overview

Sprint 3 focused on building the stock screening, composite scoring, peer comparison, and financial analytics reporting workflow for the 92-company analysis universe.

## Completed Work

- Developed a configurable filter engine supporting financial and growth-based screening metrics.
- Implemented six preset screeners:
  - Quality Compounder
  - Value Pick
  - Growth Accelerator
  - Dividend Champion
  - Debt-Free Blue Chip
  - Turnaround Watch
- Implemented a composite quality scoring model using profitability, cash quality, growth, and leverage factors.
- Applied P10/P90 winsorisation to reduce the impact of extreme financial values.
- Implemented sector-relative scoring for comparison within broad sectors.
- Developed peer percentile ranking across 11 peer groups.
- Implemented inverse percentile ranking for Debt-to-Equity, where lower leverage receives a higher rank.
- Populated the peer_percentiles table in SQLite.
- Generated company radar charts with peer-group average overlays.
- Generated screener_output.xlsx with six preset sheets and conditional formatting.
- Generated peer_comparison.xlsx with 11 peer-group sheets, percentile colour coding, benchmark highlighting, and median summary rows.

## Validation Results

- All 14 Data Quality rule unit tests passed with zero failures.
- Full project test suite passed: 96 tests passed with zero failures.
- Quality Compounder top five results were manually verified against the required thresholds.
- IT Services peer ranking was spot-checked successfully.
- TCS had the highest 2024 ROE in the IT Services peer group and correctly received a percentile rank of 1.0.
- Excel report structures and sheet counts were validated.

## Challenges and Resolutions

### Value Pick Result Count

The Value Pick preset returned 2 companies instead of the target range of 5 to 50. Diagnostic analysis confirmed that only two companies in the available dataset simultaneously satisfied the required P/E, P/B, Debt-to-Equity, and Dividend Yield thresholds. The original thresholds were preserved rather than modified only to increase the result count.

### Financial Sector Leverage

Debt-to-Equity filtering was adjusted for Financials-sector companies because high leverage is structurally normal for banks, NBFCs, and insurance companies.

### Extreme Ratio Values

Some companies showed unusually high ROE and ROCE values because of source-data and formula denominator effects. These cases were documented, and P10/P90 winsorisation was used in composite scoring to reduce distortion from extreme values.

## Key Decisions

- Preserve required screener thresholds unless changes are approved.
- Use ratio-engine values for analytics and source values only for reference or display where required.
- Use inverse percentile ranking for Debt-to-Equity.
- Use sector-relative scoring to improve comparability across different industries.
- Use peer percentile scores on a common scale for radar-chart comparison.

## Sprint Outcome

Sprint 3 delivered an end-to-end financial screening and peer analytics workflow. The system now supports configurable screening, preset investment strategies, composite quality scoring, sector-relative analysis, peer percentile rankings, radar-chart visualisation, and formatted Excel reporting.

The sprint deliverables are ready for review and demonstration.