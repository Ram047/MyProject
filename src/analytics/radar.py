import os
import sqlite3
import textwrap

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.screener.engine import load_screener_dataframe
from src.screener.scoring_export import (
    build_extra_metrics,
    calculate_composite_score,
    calculate_sector_relative_score,
)


DB_PATH = "database/stock_analysis.db"
PEER_FILE = "data/peer_groups.xlsx"
OUTPUT_DIR = "reports/radar_charts"


AXES = [
    "ROE",
    "ROCE",
    "NPM",
    "D/E",
    "FCF Score",
    "PAT CAGR 5yr",
    "Revenue CAGR 5yr",
    "Composite Score",
]


PEER_METRIC_MAP = {
    "ROE": "ROE",
    "ROCE": "ROCE",
    "NPM": "Net Profit Margin",
    "D/E": "D/E",
    "PAT CAGR 5yr": "PAT CAGR 5yr",
    "Revenue CAGR 5yr": "Revenue CAGR 5yr",
}


# ============================================================
# LOAD PEER GROUP MAPPING
# ============================================================

def load_peer_groups():

    peers = pd.read_excel(
        PEER_FILE,
        sheet_name="Sheet1"
    )

    peers = peers[
        [
            "company_id",
            "peer_group_name"
        ]
    ].drop_duplicates()

    return peers


# ============================================================
# LOAD LATEST PEER PERCENTILES
# ============================================================

def load_latest_peer_percentiles():

    conn = sqlite3.connect(
        DB_PATH
    )

    try:

        data = pd.read_sql_query(
            """
            SELECT
                company_id,
                peer_group_name,
                metric,
                value,
                percentile_rank,
                year
            FROM peer_percentiles
            """,
            conn
        )

    finally:

        conn.close()

    if data.empty:
        raise ValueError(
            "peer_percentiles table is empty. Run peer.py first."
        )

    data["year"] = pd.to_numeric(
        data["year"],
        errors="coerce"
    )

    latest_year = (
        data
        .groupby("company_id")["year"]
        .transform("max")
    )

    latest = data[
        data["year"] == latest_year
    ].copy()

    return latest


# ============================================================
# LOAD COMPOSITE SCORES
# ============================================================

def load_composite_scores():

    print(
        "Calculating latest composite scores..."
    )

    df = load_screener_dataframe(
        DB_PATH
    )

    df = build_extra_metrics(
        df
    )

    df = calculate_composite_score(
        df
    )

    df = calculate_sector_relative_score(
        df
    )

    return df


# ============================================================
# FCF SCORE
# ============================================================

def calculate_peer_fcf_scores(df, peers):

    temp = df[
        [
            "company_id",
            "free_cash_flow_cr"
        ]
    ].merge(
        peers,
        on="company_id",
        how="inner"
    )

    def percentile_score(series):

        valid_count = series.notna().sum()

        if valid_count <= 1:

            result = pd.Series(
                50.0,
                index=series.index
            )

            result[
                series.isna()
            ] = np.nan

            return result

        rank = series.rank(
            method="min",
            ascending=True
        )

        return (
            (rank - 1)
            /
            (valid_count - 1)
            *
            100
        )

    temp["fcf_score"] = (
        temp
        .groupby(
            "peer_group_name",
            group_keys=False
        )["free_cash_flow_cr"]
        .apply(percentile_score)
    )

    return temp[
        [
            "company_id",
            "peer_group_name",
            "fcf_score"
        ]
    ]


# ============================================================
# BUILD RADAR DATA
# ============================================================

def build_radar_dataframe():

    peers = load_peer_groups()

    percentile_data = (
        load_latest_peer_percentiles()
    )

    scores = load_composite_scores()

    fcf_scores = calculate_peer_fcf_scores(
        scores,
        peers
    )

    records = []

    for _, peer_row in peers.iterrows():

        company_id = peer_row[
            "company_id"
        ]

        peer_group = peer_row[
            "peer_group_name"
        ]

        company_percentiles = (
            percentile_data[
                percentile_data[
                    "company_id"
                ] == company_id
            ]
        )

        score_row = scores[
            scores["company_id"]
            == company_id
        ]

        fcf_row = fcf_scores[
            fcf_scores["company_id"]
            == company_id
        ]

        if score_row.empty:
            continue

        record = {
            "company_id": company_id,
            "peer_group_name": peer_group
        }

        for axis_name, metric_name in (
            PEER_METRIC_MAP.items()
        ):

            metric_row = company_percentiles[
                company_percentiles["metric"]
                == metric_name
            ]

            if metric_row.empty:

                record[axis_name] = np.nan

            else:

                percentile = metric_row.iloc[
                    0
                ]["percentile_rank"]

                record[axis_name] = (
                    percentile * 100
                    if pd.notna(percentile)
                    else np.nan
                )

        if fcf_row.empty:

            record["FCF Score"] = np.nan

        else:

            record["FCF Score"] = (
                fcf_row.iloc[0][
                    "fcf_score"
                ]
            )

        record["Composite Score"] = (
            score_row.iloc[0][
                "composite_quality_score"
            ]
        )

        records.append(record)

    return pd.DataFrame(records), scores, peers


# ============================================================
# RADAR CHART
# ============================================================

def create_peer_radar(
    company_id,
    company_values,
    peer_average,
    peer_group
):

    values = company_values.copy()
    averages = peer_average.copy()

    values = np.nan_to_num(
        values,
        nan=50.0
    )

    averages = np.nan_to_num(
        averages,
        nan=50.0
    )

    number_of_axes = len(AXES)

    angles = np.linspace(
        0,
        2 * np.pi,
        number_of_axes,
        endpoint=False
    ).tolist()

    values = values.tolist()
    averages = averages.tolist()

    angles += angles[:1]
    values += values[:1]
    averages += averages[:1]

    fig = plt.figure(
        figsize=(10, 8)
    )

    ax = fig.add_subplot(
        111,
        polar=True
    )

    ax.plot(
        angles,
        values,
        linewidth=2.5,
        label=company_id
    )

    ax.fill(
        angles,
        values,
        alpha=0.25
    )

    ax.plot(
        angles,
        averages,
        linewidth=2,
        linestyle="--",
        label=f"{peer_group} Average"
    )

    ax.set_xticks(
        angles[:-1]
    )

    ax.set_xticklabels(
        [
            textwrap.fill(label, 14)
            for label in AXES
        ],
        fontsize=10
    )

    ax.set_ylim(
        0,
        100
    )

    ax.set_yticks(
        [20, 40, 60, 80, 100]
    )

    ax.set_yticklabels(
        ["20", "40", "60", "80", "100"],
        fontsize=9
    )

    ax.set_title(
        f"{company_id} Peer Radar\n{peer_group}",
        fontsize=16,
        pad=25
    )

    ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.35, 1.15),
        fontsize=10
    )

    plt.tight_layout()

    output_path = os.path.join(
        OUTPUT_DIR,
        f"{company_id}_radar.png"
    )

    plt.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close(fig)

    return output_path


# ============================================================
# UNASSIGNED COMPANY CHART
# ============================================================

def create_standalone_chart(
    company_id,
    company_score,
    nifty_average
):

    fig = plt.figure(
        figsize=(8, 6)
    )

    ax = fig.add_subplot(111)

    labels = [
        company_id,
        "Nifty 100 Average"
    ]

    values = [
        company_score,
        nifty_average
    ]

    bars = ax.bar(
        labels,
        values
    )

    ax.set_ylim(
        0,
        100
    )

    ax.set_ylabel(
        "Composite Quality Score",
        fontsize=12
    )

    ax.set_title(
        f"{company_id} Standalone Score Comparison",
        fontsize=15,
        pad=15
    )

    ax.tick_params(
        axis="x",
        labelsize=11
    )

    ax.tick_params(
        axis="y",
        labelsize=10
    )

    for bar, value in zip(
        bars,
        values
    ):

        ax.text(
            bar.get_x()
            +
            bar.get_width() / 2,

            bar.get_height() + 1,

            f"{value:.2f}",

            ha="center",
            fontsize=11
        )

    plt.tight_layout()

    output_path = os.path.join(
        OUTPUT_DIR,
        f"{company_id}_radar.png"
    )

    plt.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close(fig)

    return output_path


# ============================================================
# GENERATE ALL CHARTS
# ============================================================

def generate_all_charts():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    print("=" * 70)
    print("RADAR CHART GENERATOR")
    print("=" * 70)

    radar_df, scores, peers = (
        build_radar_dataframe()
    )

    print(
        f"\nPeer-assigned companies: "
        f"{radar_df['company_id'].nunique()}"
    )

    generated = 0

    # ========================================================
    # PEER GROUP RADAR CHARTS
    # ========================================================

    for peer_group, group in (
        radar_df.groupby(
            "peer_group_name"
        )
    ):

        peer_average = (
            group[AXES]
            .mean()
            .values
        )

        for _, row in group.iterrows():

            company_values = (
                row[AXES]
                .astype(float)
                .values
            )

            create_peer_radar(
                row["company_id"],
                company_values,
                peer_average,
                peer_group
            )

            generated += 1

    # ========================================================
    # COMPANIES WITHOUT PEER GROUP
    # ========================================================

    assigned_companies = set(
        peers["company_id"]
    )

    all_companies = set(
        scores["company_id"]
    )

    unassigned = sorted(
        all_companies
        -
        assigned_companies
    )

    nifty_average = (
        scores[
            "composite_quality_score"
        ]
        .mean()
    )

    print(
        f"Companies without peer group: "
        f"{len(unassigned)}"
    )

    for company_id in unassigned:

        company_row = scores[
            scores["company_id"]
            == company_id
        ]

        if company_row.empty:
            continue

        company_score = (
            company_row.iloc[0][
                "composite_quality_score"
            ]
        )

        create_standalone_chart(
            company_id,
            company_score,
            nifty_average
        )

        generated += 1

    print(
        f"\nCharts generated: {generated}"
    )

    print(
        f"Output folder: {OUTPUT_DIR}"
    )

    return generated


# ============================================================
# SINGLE COMPANY LOOKUP
# ============================================================

def generate_company_chart(company_id):

    company_id = str(
        company_id
    ).upper()

    radar_df, scores, peers = (
        build_radar_dataframe()
    )

    company_data = radar_df[
        radar_df["company_id"]
        == company_id
    ]

    if not company_data.empty:

        row = company_data.iloc[0]

        peer_group = row[
            "peer_group_name"
        ]

        peer_data = radar_df[
            radar_df["peer_group_name"]
            == peer_group
        ]

        peer_average = (
            peer_data[AXES]
            .mean()
            .values
        )

        company_values = (
            row[AXES]
            .astype(float)
            .values
        )

        return create_peer_radar(
            company_id,
            company_values,
            peer_average,
            peer_group
        )

    score_row = scores[
        scores["company_id"]
        == company_id
    ]

    if score_row.empty:

        return (
            f"Company {company_id} not found"
        )

    print(
        "No peer group assigned — "
        "generating standalone chart."
    )

    nifty_average = (
        scores[
            "composite_quality_score"
        ]
        .mean()
    )

    company_score = (
        score_row.iloc[0][
            "composite_quality_score"
        ]
    )

    return create_standalone_chart(
        company_id,
        company_score,
        nifty_average
    )


# ============================================================
# MAIN
# ============================================================

def main():

    generated = generate_all_charts()

    print(
        "\nProcessing complete."
    )

    print(
        f"Total PNG files created: "
        f"{generated}"
    )


if __name__ == "__main__":

    main()