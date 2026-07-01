def calculate_cagr(start, end, years):
    """
    Calculate CAGR and return (value, flag)
    """

    if years <= 0:
        return None, "INSUFFICIENT"

    if start == 0:
        return None, "ZERO_BASE"

    if start > 0 and end > 0:
        cagr = ((end / start) ** (1 / years) - 1) * 100
        return round(cagr, 2), None

    if start > 0 and end < 0:
        return None, "DECLINE_TO_LOSS"

    if start < 0 and end > 0:
        return None, "TURNAROUND"

    if start < 0 and end < 0:
        return None, "BOTH_NEGATIVE"

    return None, None


def revenue_cagr(start, end, years):
    return calculate_cagr(start, end, years)


def pat_cagr(start, end, years):
    return calculate_cagr(start, end, years)


def eps_cagr(start, end, years):
    return calculate_cagr(start, end, years)


def insufficient_data(total_years, required_years):
    if total_years < required_years:
        return None, "INSUFFICIENT"

    return True, None