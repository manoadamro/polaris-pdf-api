from datetime import date, timedelta
from typing import Dict

from faker import Faker

METRIC_NAMES = [
    "count_obs_missing_acvpu",
    "count_obs_missing_hr",
    "count_obs_missing_hr_pat_refused",
    "count_obs_missing_o2therapy",
    "count_obs_missing_rr",
    "count_obs_missing_rr_pat_refused",
    "count_obs_missing_sbp",
    "count_obs_missing_sbp_pat_refused",
    "count_obs_missing_spo2",
    "count_obs_missing_spo2_pat_refused",
    "count_obs_missing_temperature",
    "count_obs_missing_temperature_pat_refused",
    "count_obs_sets_complete",
    "count_obs_sets_late_high_risk",
    "count_obs_sets_late_lomed_risk",
    "count_obs_sets_late_low_risk",
    "count_obs_sets_late_med_risk",
    "count_obs_sets_late_zero_risk",
    "count_obs_sets_on_time_high_risk",
    "count_obs_sets_on_time_lomed_risk",
    "count_obs_sets_on_time_low_risk",
    "count_obs_sets_on_time_med_risk",
    "count_obs_sets_on_time_zero_risk",
    "count_obs_sets_partial",
]


def generate_ward_report(
    days: int = 1, locale: str = "en_GB", force_zero: bool = False
) -> Dict:
    fake: Faker = Faker(locale)
    timestamp = fake.date(pattern="%Y-%m-%dT%H:%M:%S.000")
    base_date: date = date.fromisoformat(timestamp[:10])
    pdf_data = [
        {
            "measurement_timestamp": timestamp,
            "metric_date": (base_date + timedelta(days=day - 1)).isoformat(),
            "metric_name": m,
            "metric_value": 0 if force_zero else fake.random_int(min=0, max=150),
        }
        for day in range(days)
        for m in METRIC_NAMES
    ]

    return {
        "hospital_name": f"{fake.last_name()} Hospital",
        "ward_name": f"{fake.first_name()} Ward",
        "report_month": fake.month_name(),
        "report_year": fake.year(),
        "location_uuid": fake.uuid4(),
        "message_create_date": timestamp,
        "message_name": fake.sentence(),
        "pdf_data": pdf_data,
    }
