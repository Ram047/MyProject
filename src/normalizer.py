def normalize_year(year):
    """
    Normalize a year value to an integer.
    """
    if year is None:
        return None

    year = str(year).strip()

    if len(year) == 4 and year.isdigit():
        return int(year)

    raise ValueError("Invalid year format")


def normalize_ticker(ticker):
    """
    Normalize a stock ticker symbol.
    """
    if ticker is None:
        return None

    return ticker.strip().upper()