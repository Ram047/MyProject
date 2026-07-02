import csv
import os


def free_cash_flow(operating_activity, investing_activity):
    """
    FCF = CFO + CFI
    """
    return operating_activity + investing_activity


def cfo_quality_score(cfo, pat):
    """
    CFO / PAT ratio
    """
    if pat == 0:
        return None

    score = cfo / pat

    if score > 1.0:
        return score, "High Quality"
    elif score >= 0.5:
        return score, "Moderate"
    else:
        return score, "Accrual Risk"


def capex_intensity(investing_activity, sales):
    """
    CapEx Intensity = abs(CFI) / Sales * 100
    """
    if sales == 0:
        return None, None

    value = abs(investing_activity) / sales * 100

    if value < 3:
        label = "Asset Light"
    elif value <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"

    return round(value, 2), label


def fcf_conversion_rate(fcf, operating_profit):
    """
    FCF / Operating Profit * 100
    """
    if operating_profit == 0:
        return None

    return round((fcf / operating_profit) * 100, 2)


def capital_allocation_pattern(cfo, cfi, cff, cfo_pat_ratio=None):
    """
    Capital allocation classifier
    """

    signs = (
        "+" if cfo >= 0 else "-",
        "+" if cfi >= 0 else "-",
        "+" if cff >= 0 else "-"
    )

    if signs == ("+", "-", "-"):
        if cfo_pat_ratio is not None and cfo_pat_ratio > 1:
            return "Shareholder Returns"
        return "Reinvestor"

    if signs == ("+", "+", "-"):
        return "Liquidating Assets"

    if signs == ("-", "+", "+"):
        return "Distress Signal"

    if signs == ("-", "-", "+"):
        return "Growth Funded by Debt"

    if signs == ("+", "+", "+"):
        return "Cash Accumulator"

    if signs == ("-", "-", "-"):
        return "Pre-Revenue"

    if signs == ("+", "-", "+"):
        return "Mixed"

    return "Unknown"


def generate_capital_allocation_csv(records, output_path="output/capital_allocation.csv"):
    """
    Generate CSV with capital allocation patterns.
    """

    os.makedirs("output", exist_ok=True)

    with open(output_path, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "company_id",
            "year",
            "cfo_sign",
            "cfi_sign",
            "cff_sign",
            "pattern_label"
        ])

        for record in records:
            company_id, year, cfo, cfi, cff, label = record

            writer.writerow([
                company_id,
                year,
                "+" if cfo >= 0 else "-",
                "+" if cfi >= 0 else "-",
                "+" if cff >= 0 else "-",
                label
            ])