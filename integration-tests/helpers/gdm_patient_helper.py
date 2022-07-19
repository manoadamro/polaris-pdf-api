from typing import Dict

from faker import Faker


def generate_gdm_patient() -> Dict:
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
            "record": {
                "history": {"parity": 3, "gravidity": 4},
                "notes": [
                    {
                        "clinician": {
                            "created": "2021-11-22T02:32:02.772Z",
                            "email_address": "g.cardano@mail.com",
                            "first_name": "Gerolamo",
                            "job_title": "midwife",
                            "last_name": "Cardano",
                            "uuid": "gdm_clinician_uuid",
                        },
                        "content": "Reminded patients to add comments to blood glucose readings",
                        "created": "2021-11-04T22:02:10.579Z",
                        "created_by": {
                            "first_name": "Gerolamo",
                            "last_name": "Cardano",
                            "uuid": "gdm_clinician_uuid",
                        },
                        "modified": "2021-11-22:34:13.503Z",
                        "modified_by": {
                            "first_name": "Gerolamo",
                            "last_name": "Cardano",
                            "uuid": "gdm_clinician_uuid",
                        },
                        "uuid": "f29dad58-a8bf-488d-a8c8-e89d09de4809",
                    },
                    {
                        "clinician": {
                            "created": "2021-11-22T03:32:02.772Z",
                            "email_address": "g.cardano@mail.com",
                            "first_name": "Gerolamo",
                            "job_title": "midwife",
                            "last_name": "Cardano",
                            "uuid": "gdm_clinician_uuid",
                        },
                        "content": "Patients readings are going up and down",
                        "created": "2021-11-04T22:02:10.579Z",
                        "created_by": {
                            "first_name": "Gerolamo",
                            "last_name": "Cardano",
                            "uuid": "gdm_clinician_uuid",
                        },
                        "modified": "2021-11-22:34:13.503Z",
                        "modified_by": {
                            "first_name": "Gerolamo",
                            "last_name": "Cardano",
                            "uuid": "gdm_clinician_uuid",
                        },
                        "uuid": "f29dad58-a8bf-488d-a8c8-e89d09de4810",
                    },
                ],
            },
        },
        "pregnancy": {"some": "value"},
        "readings_plan": {"some": "value"},
        "management_plan": {"some": "value"},
        "diabetes": {
            "first_hba1c": {"value": 5, "date": "2001-01-01"},
            "latest_hba1c": {"value": 7, "date": "2001-01-01"},
        },
        "deliveries": [
            {
                "patient": {
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                }
            }
        ],
        "blood_glucose_readings": [{"some": "value"}],
        "latest_visit": {"some": "value"},
        "medication_plan": {"some": "value"},
        "post_natal_reading": {"date": "2001-03-02", "value": None},
        "messages": [
            {
                "confirmed": None,
                "content": "Testing first message",
                "created": "2021-12-23 10:26:48",
                "created_by": "static_clinician_uuid_A",
                "clinician": {
                    "first_name": "Tiani",
                    "last_name": "Hilli",
                    "job_title": "Assistant",
                },
                "message_type": {
                    "created": "2020-01-21T17:02:34.617Z",
                    "created_by": "sys",
                    "modified": "2020-01-21T17:02:34.617Z",
                    "modified_by": "sys",
                    "uuid": "DHOS-MESSAGES-GENERAL",
                    "value": 0,
                },
            },
            {
                "confirmed": None,
                "content": "Testing second message",
                "created": "2021-12-23 10:26:48",
                "created_by": "sys",
                "message_type": {
                    "created": "2020-01-21T17:02:34.617Z",
                    "created_by": "sys",
                    "modified": "2020-01-21T17:02:34.617Z",
                    "modified_by": "sys",
                    "uuid": "DHOS-MESSAGES-GENERAL",
                    "value": 0,
                },
            },
        ],
    }
