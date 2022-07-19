from marshmallow import fields

from dhos_pdf_api.models.diabetes_patient import (
    PatientSchema as diabetes_patient_schema,
)


class PatientSchema(diabetes_patient_schema):
    created = fields.String(required=False, allow_none=True)
