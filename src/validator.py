import os
import pandas as pd


def validate(df, dataset_name="dataset"):
    failures = []

    # DQ-01: Primary Key (id) should not be null
    if "id" in df.columns:
        null_ids = df[df["id"].isnull()]
        for index in null_ids.index:
            failures.append([
                dataset_name,
                index,
                "DQ-01",
                "CRITICAL",
                "Primary Key (id) is missing"
            ])

    # DQ-02: Duplicate Primary Key
    if "id" in df.columns:
        duplicates = df[df["id"].duplicated()]
        for index in duplicates.index:
            failures.append([
                dataset_name,
                index,
                "DQ-02",
                "CRITICAL",
                "Duplicate Primary Key"
            ])

    # DQ-03: company_id should not be null
    if "company_id" in df.columns:
        missing_company = df[df["company_id"].isnull()]
        for index in missing_company.index:
            failures.append([
                dataset_name,
                index,
                "DQ-03",
                "CRITICAL",
                "Missing company_id"
            ])

    # DQ-04: Sales should not be negative
    if "sales" in df.columns:
        negative_sales = df[df["sales"] < 0]
        for index in negative_sales.index:
            failures.append([
                dataset_name,
                index,
                "DQ-04",
                "WARNING",
                "Negative sales value"
            ])

    # DQ-05: OPM should be between 0 and 100
    if "opm_percentage" in df.columns:
        invalid_opm = df[
            (df["opm_percentage"] < 0) |
            (df["opm_percentage"] > 100)
        ]

        for index in invalid_opm.index:
            failures.append([
                dataset_name,
                index,
                "DQ-05",
                "WARNING",
                "Invalid OPM Percentage"
            ])

    failure_df = pd.DataFrame(
        failures,
        columns=[
            "Dataset",
            "Row",
            "Rule",
            "Severity",
            "Message"
        ]
    )

    os.makedirs("output", exist_ok=True)

    failure_df.to_csv(
        "output/validation_failures.csv",
        index=False
    )

    return failure_df