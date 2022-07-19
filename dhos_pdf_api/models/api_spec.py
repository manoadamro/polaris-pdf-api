from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask_batteries_included.helpers.apispec import (
    FlaskBatteriesPlugin,
    initialise_apispec,
    openapi_schema,
)
from marshmallow import EXCLUDE, Schema, fields

from dhos_pdf_api.models import diabetes_patient
from dhos_pdf_api.models import pregnancy as patient_pregnancy
from dhos_pdf_api.models import send_pdf_data, trustomer_config
from dhos_pdf_api.models.dbm_patient import PatientSchema

dhos_pdf_api_spec: APISpec = APISpec(
    version="1.0.1",
    openapi_version="3.0.3",
    title="DHOS PDF API",
    info={
        "description": "The DHOS PDF API is responsible for storing and retrieving PDF documents."
    },
    plugins=[FlaskPlugin(), MarshmallowPlugin(), FlaskBatteriesPlugin()],
)
initialise_apispec(dhos_pdf_api_spec)


@openapi_schema(dhos_pdf_api_spec, {"nullable": True})
class LocationSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    ods_code = fields.String(required=True)
    display_name = fields.String(required=True)
    location_type = fields.String(required=True)
    parent = fields.Nested("LocationSchema", required=False, allow_none=True)


@openapi_schema(dhos_pdf_api_spec)
class SendPdfRequestSchema(Schema):
    class Meta:
        title = "Send report request data"
        unknown = EXCLUDE
        ordered = True

    patient = fields.Nested(send_pdf_data.PatientSchema, required=True)
    encounter = fields.Nested(send_pdf_data.EncounterSchema, required=True)
    location = fields.Nested(LocationSchema, required=True)
    observation_sets = fields.List(
        fields.Nested(send_pdf_data.ObservationSetSchema), required=True
    )


@openapi_schema(dhos_pdf_api_spec)
class WardReportRequestSchema(Schema):
    class Meta:
        title = "Ward report request data"
        unknown = EXCLUDE
        ordered = True

    hospital_name = fields.String(
        metadata={
            "description": "Name of hospital",
            "example": "Birchy Hospital",
        },
        required=True,
    )
    ward_name = fields.String(
        metadata={
            "description": "Name of ward",
            "example": "Dumbledore Ward",
        },
        required=True,
    )
    location_uuid = fields.UUID(
        metadata={
            "description": "UUID of ward location",
            "example": "7379e212-9bab-4df1-a95f-f927c4c9f7f1",
        },
    )
    report_month = fields.String(
        metadata={
            "description": "Month of report",
            "example": "July",
        },
        required=True,
    )
    report_year = fields.String(
        metadata={
            "description": "Year of report",
            "example": "2019",
        },
        required=True,
    )
    pdf_data = fields.List(fields.Nested(send_pdf_data.MetricSchema), required=True)


@openapi_schema(dhos_pdf_api_spec)
class GdmPdfRequestSchema(Schema):
    class Meta:
        title = "Patient report request data"
        unknown = EXCLUDE
        ordered = True

    patient = fields.Nested(patient_pregnancy.PatientSchema, required=True)
    pregnancy = fields.Nested(patient_pregnancy.PregnancySchema, required=True)
    readings_plan = fields.Nested(diabetes_patient.ReadingsPlanSchema, required=True)
    deliveries = fields.List(
        fields.Nested(patient_pregnancy.DeliverySchema), required=True
    )
    latest_visit = fields.Nested(diabetes_patient.LatestVisitSchema, required=True)
    management_plan = fields.Nested(diabetes_patient.ManagementPlan, required=True)
    blood_glucose_readings = fields.List(
        fields.Nested(diabetes_patient.BloodGlucoseReading), required=True
    )
    diabetes = fields.Nested(diabetes_patient.Diabetes, required=True)

    medications = fields.Dict(keys=fields.String(), required=True)
    medication_plan = fields.Dict(keys=fields.String(), required=True)
    post_natal_reading = fields.Nested(
        patient_pregnancy.PostNatalReading, required=True
    )
    messages = fields.List(fields.Dict(), required=True, allow_none=True)


@openapi_schema(dhos_pdf_api_spec)
class DbmPdfRequestSchema(Schema):
    class Meta:
        title = "Patient report request data"
        unknown = EXCLUDE
        ordered = True

    patient = fields.Nested(PatientSchema, required=True)
    readings_plan = fields.Nested(diabetes_patient.ReadingsPlanSchema, required=True)
    management_plan = fields.Nested(diabetes_patient.ManagementPlan, required=True)
    blood_glucose_readings = fields.List(
        fields.Nested(diabetes_patient.BloodGlucoseReading), required=True
    )
    diabetes = fields.Nested(diabetes_patient.Diabetes, required=True)
    medications = fields.Dict(keys=fields.String(), required=True)
    medication_plan = fields.Dict(keys=fields.String(), required=True)
    hba1c_details = fields.Dict(keys=fields.String(), required=False, allow_none=True)


class SendPdfDataSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    patient = fields.Nested(send_pdf_data.PatientSchema, required=True)
    encounter = fields.Nested(send_pdf_data.EncounterSchema, required=True)
    location = fields.Nested(LocationSchema, required=True)
    observation_sets = fields.List(
        fields.Nested(send_pdf_data.ObservationSetSchema), required=True
    )
    trustomer = fields.Nested(trustomer_config.TrustomerConfigSchema, required=True)
