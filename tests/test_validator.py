import pandas as pd

from src.validator import validate


# ============================================================
# DQ-01: PRIMARY KEY NOT NULL
# ============================================================

def test_dq01_valid_id():
    df = pd.DataFrame({
        "id": [1, 2, 3]
    })

    result = validate(df, "test")

    assert "DQ-01" not in result["Rule"].values


def test_dq01_null_id():
    df = pd.DataFrame({
        "id": [1, None, 3]
    })

    result = validate(df, "test")

    assert "DQ-01" in result["Rule"].values


def test_dq01_severity_critical():
    df = pd.DataFrame({
        "id": [None]
    })

    result = validate(df, "test")

    row = result[
        result["Rule"] == "DQ-01"
    ].iloc[0]

    assert row["Severity"] == "CRITICAL"


# ============================================================
# DQ-02: DUPLICATE PRIMARY KEY
# ============================================================

def test_dq02_unique_ids():
    df = pd.DataFrame({
        "id": [1, 2, 3]
    })

    result = validate(df, "test")

    assert "DQ-02" not in result["Rule"].values


def test_dq02_duplicate_id():
    df = pd.DataFrame({
        "id": [1, 2, 2]
    })

    result = validate(df, "test")

    assert "DQ-02" in result["Rule"].values


def test_dq02_only_duplicate_occurrence_flagged():
    df = pd.DataFrame({
        "id": [1, 1]
    })

    result = validate(df, "test")

    duplicate_rows = result[
        result["Rule"] == "DQ-02"
    ]

    assert len(duplicate_rows) == 1


# ============================================================
# DQ-03: COMPANY ID NOT NULL
# ============================================================

def test_dq03_valid_company_id():
    df = pd.DataFrame({
        "company_id": ["TCS", "INFY"]
    })

    result = validate(df, "test")

    assert "DQ-03" not in result["Rule"].values


def test_dq03_missing_company_id():
    df = pd.DataFrame({
        "company_id": ["TCS", None]
    })

    result = validate(df, "test")

    assert "DQ-03" in result["Rule"].values


def test_dq03_severity_critical():
    df = pd.DataFrame({
        "company_id": [None]
    })

    result = validate(df, "test")

    row = result[
        result["Rule"] == "DQ-03"
    ].iloc[0]

    assert row["Severity"] == "CRITICAL"


# ============================================================
# DQ-04: SALES MUST NOT BE NEGATIVE
# ============================================================

def test_dq04_positive_sales():
    df = pd.DataFrame({
        "sales": [1000, 2000]
    })

    result = validate(df, "test")

    assert "DQ-04" not in result["Rule"].values


def test_dq04_negative_sales():
    df = pd.DataFrame({
        "sales": [1000, -500]
    })

    result = validate(df, "test")

    assert "DQ-04" in result["Rule"].values


def test_dq04_zero_sales_allowed():
    df = pd.DataFrame({
        "sales": [0]
    })

    result = validate(df, "test")

    assert "DQ-04" not in result["Rule"].values


# ============================================================
# DQ-05: OPM RANGE 0 TO 100
# ============================================================

def test_dq05_valid_opm():
    df = pd.DataFrame({
        "opm_percentage": [0, 25, 100]
    })

    result = validate(df, "test")

    assert "DQ-05" not in result["Rule"].values


def test_dq05_invalid_opm():
    df = pd.DataFrame({
        "opm_percentage": [-1, 101]
    })

    result = validate(df, "test")

    invalid_rows = result[
        result["Rule"] == "DQ-05"
    ]

    assert len(invalid_rows) == 2