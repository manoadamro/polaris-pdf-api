from typing import Dict

from faker import Faker


def generate_dbm_patient() -> Dict:
    fake = Faker()
    return {
        "medications": {"some": "value"},
        "patient": {
            "uuid": fake.uuid4(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "nhs_number": str(fake.random_number(digits=10, fix_len=True)),
            "hospital_number": str(fake.random_number(digits=10, fix_len=True)),
            "personal_address": {"postcode": "AB12 CD"},
        },
        "readings_plan": {"some": "value"},
        "management_plan": {"some": "value"},
        "diabetes": {
            "first_hba1c": {"value": 5, "date": "2001-01-01"},
            "latest_hba1c": {"value": 7, "date": "2001-01-01"},
        },
        "blood_glucose_readings": [
            {
                "measured_timestamp": "2021-08-29 20:40:07.498",
                "blood_glucose_value": 4.5,
                "comment": "here's a comment",
            }
        ],
        "latest_visit": {"some": "value"},
        "medication_plan": {"some": "value"},
        "hba1c_details": {
            "readings": [
                {
                    "date_observed": "2021-02-20",
                    "units": "mmol/mol",
                    "uuid": "1cc16c69-c5fc-4a71-b194-c945262c9332",
                    "value": 29.0,
                }
            ]
        },
    }
