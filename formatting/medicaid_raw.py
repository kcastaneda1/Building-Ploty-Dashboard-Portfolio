from load_data.medicaid_api import get_medicaid_data
import numpy as np
import pandas as pd 

def clean_dataset(limit=1000):
    # Retrieve data from CMS API
    df = get_medicaid_data(limit = limit)

    # Preserve the API response
    raw_df = df.copy()

    # Create working DataFrame
    clean_df = raw_df.copy()

    #----------------------
    # DATA CLEANUP AND VALIDATE
    #----------------------

    # 1. Valiadte required columns

    required_columns = [
        "state_abbreviation",
        "state_name",
        "reporting_period",
        "preliminary_or_updated",
        "final_report"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in clean_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # 2. Replace blank/whitespace-only values with NaN
    clean_df = clean_df.replace(
        r"^\s*$",
        np.nan,
        regex=True
    )

    # Replace * and ** values with NaN
    clean_df = clean_df.replace(
        r"^\s*\*=\s*$",
        np.nan,
        regex=True
    )

    # Create Analytical reporting data
    clean_df["reporting_date"] = pd.to_datetime(
        clean_df['reporting_period']
        .astype(str)
        .str.strip(),
        format="%Y%m",
        errors="coerce"
    )

    # numeric columns
    numeric_columns = [
        "new_applications_submitted_to_medicaid_and_chip_agencies",
        "applications_for_financial_assistance_submitted_to_the_stat_104d",
        "total_applications_for_financial_assistance_submitted_at_st_d6fa",
        "individuals_determined_eligible_for_medicaid_at_application",
        "individuals_determined_eligible_for_chip_at_application",
        "total_medicaid_and_chip_determinations",
        "medicaid_and_chip_child_enrollment",
        "total_medicaid_and_chip_enrollment",
        "total_medicaid_enrollment",
        "total_chip_enrollment",
        "total_adult_medicaid_enrollment",
        "total_medicaid_and_chip_determinations_processed_in_less_th_1e84",
        "total_medicaid_and_chip_determinations_processed_between_24_756e",
        "total_medicaid_and_chip_determinations_processed_between_8__a7a5",
        "total_medicaid_and_chip_determinations_processed_between_31_a42c",
        "total_medicaid_and_chip_determinations_processed_in_more_th_a7ec",
        "total_call_center_volume_number_of_calls",
        "average_call_center_wait_time_minutes",
        "average_call_center_abandonment_rate"
    ]

    # Maker sure expected numeric columns exist
    missing_numeric_columns = [
        col for col in numeric_columns
        if col not in clean_df.columns
    ]

    if missing_numeric_columns:
        raise ValueError(
            f"Missing numeric column: {missing_numeric_columns}"
        )


    # Conver numeric fields
    for col in numeric_columns:
        clean_df[col] = pd.DataFrame(
            clean_df[col],
            errors = 'coerce'
        )

    return clean_df