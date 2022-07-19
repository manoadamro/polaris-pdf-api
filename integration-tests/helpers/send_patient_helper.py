from typing import Dict

from faker import Faker


def generate_send_patient() -> Dict:
    fake = Faker()

    return {
        "encounter": {
            "uuid": fake.uuid4(),
            "created": "2020-07-23T14:50:24.424Z",
            "admitted_at": "2020-07-23T14:50:24.424Z",
            "score_system_history": [
                {
                    "changed_by": {
                        "first_name": fake.first_name(),
                        "last_name": fake.last_name(),
                        "uuid": fake.uuid4(),
                    },
                    "changed_time": "2020-07-23T14:50:24.424Z",
                    "score_system": "news2",
                    "spo2_scale": 0,
                }
            ],
        },
        "location": {
            "display_name": f"{fake.city()} Ward",
            "location_type": "225746001",
            "ods_code": "FAKE_ODS",
        },
        "observation_sets": [
            {
                "created_by": {"first_name": "Stan", "last_name": "Lee", "uuid": "G"},
                "is_partial": True,
                "observations": [
                    {
                        "measured_time": "2020-07-23T14:50:24.424Z",
                        "observation_type": "temperature",
                        "observation_unit": "celsius",
                        "observation_value": 37,
                        "patient_refused": False,
                        "score_value": 0,
                    },
                    {
                        "measured_time": "2020-07-23T14:50:24.424Z",
                        "observation_type": "nurse_concern",
                        "observation_string": "Airway compromise",
                        "observation_unit": "",
                        "patient_refused": False,
                        "score_value": None,
                    },
                ],
                "record_time": "2020-07-23T14:50:24.424Z",
                "score_severity": "string",
                "score_system": "string",
                "score_string": "0C",
                "score_value": 0,
                "spo2_scale": 0,
            }
        ],
        "patient": {
            "dob": fake.date(pattern="%Y-%m-%d"),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "nhs_number": str(fake.random_number(digits=10, fix_len=True)),
            "hospital_number": str(fake.random_number(digits=10, fix_len=True)),
        },
    }
