from marshmallow import EXCLUDE, Schema, fields

from dhos_pdf_api.models.diabetes_patient import (
    PatientSchema as diabetes_patient_schema,
)


class RecordHistorySchema(Schema):
    class Meta:
        title = "Patient record history"
        unknown = EXCLUDE
        ordered = True

    parity = fields.Integer(required=False, allow_none=True)
    gravidity = fields.Integer(required=False, allow_none=True)


class ClinicianSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    job_title = fields.String(required=False, allow_none=True)
    uuid = fields.String(required=True)


class NoteSchema(Schema):
    class Meta:
        title = "Clinician notes"
        unknown = EXCLUDE
        ordered = True

    created = fields.String(required=True)
    clinician = fields.Nested(ClinicianSchema, required=False, allow_none=True)
    content = fields.String(required=False, allow_none=True)


class RecordSchema(Schema):
    class Meta:
        title = "Patient record"
        unknown = EXCLUDE
        ordered = True

    history = fields.Nested(RecordHistorySchema, required=False, allow_none=True)
    notes = fields.List(fields.Nested(NoteSchema), required=False, allow_none=True)


class PatientSchema(diabetes_patient_schema):
    record = fields.Nested(RecordSchema, required=False, allow_none=True)


class BabySchema(Schema):
    class Meta:
        title = "Baby data"
        unknown = EXCLUDE
        ordered = True

    first_name = fields.String(required=False, allow_none=True)
    last_name = fields.String(required=False, allow_none=True)
    sex = fields.String(required=False, allow_none=True)
    dob = fields.String(required=False, allow_none=True)


class PostNatalReading(Schema):
    class Meta:
        title = "Post natal reading"
        unknown = EXCLUDE
        ordered = True

    value = fields.Field(required=False, allow_none=True)
    date = fields.String(required=False, allow_none=True)


class PregnancySchema(Schema):
    class Meta:
        title = "Patient pregnancy"
        unknown = EXCLUDE
        ordered = True

    stage = fields.Field(required=False, allow_none=True)
    estimated_delivery_date = fields.String(required=False, allow_none=True)
    expected_number_of_babies = fields.Integer(
        required=False,
        allow_none=True,
    )
    planned_delivery_place = fields.String(
        required=False,
        allow_none=True,
    )
    height_at_booking_in_mm = fields.Integer(
        required=False,
        allow_none=True,
    )
    weight_at_booking_in_g = fields.Integer(
        required=False,
        allow_none=True,
    )
    weight_at_diagnosis_in_g = fields.Integer(
        required=False,
        allow_none=True,
    )
    weight_at_36_weeks_in_g = fields.Integer(
        required=False,
        allow_none=True,
    )
    height_at_booking_in_cm = fields.Float(
        required=False,
        allow_none=True,
    )
    weight_at_booking_in_kg = fields.Float(
        required=False,
        allow_none=True,
    )
    weight_at_diagnosis_in_kg = fields.Float(
        required=False,
        allow_none=True,
    )
    weight_at_36_weeks_in_kg = fields.Float(
        required=False,
        allow_none=True,
    )
    colostrum_harvesting = fields.Boolean(
        required=False,
        allow_none=True,
    )
    induced = fields.Boolean(
        required=False,
        allow_none=True,
    )
    length_of_postnatal_stay_in_days = fields.Integer(
        required=False,
        allow_none=True,
    )
    post_natal_test_date = fields.String(required=False, allow_none=True)

    gestationalHypertension = fields.Boolean(required=False, allow_none=True)
    preEclampsia = fields.Boolean(required=False, allow_none=True)
    perinealTrauma = fields.Boolean(required=False, allow_none=True)
    postpartumHaemorrhage = fields.Boolean(required=False, allow_none=True)
    postpartumInfection = fields.Boolean(required=False, allow_none=True)


class DeliverySchema(Schema):
    class Meta:
        title = "Patient delivery"
        unknown = EXCLUDE
        ordered = True

    patient = fields.Nested(BabySchema, required=True)
    birth_outcome = fields.String(
        required=False,
        allow_none=True,
    )
    outcome_for_baby = fields.String(
        required=False,
        allow_none=True,
    )
    birth_weight_in_grams = fields.Integer(required=False, allow_none=True)
    admitted_to_special_baby_care_unit = fields.Field(required=False, allow_none=True)
    hypoglycemia = fields.Boolean(required=False, allow_none=True)
    hyperbilirubinemia = fields.Boolean(required=False, allow_none=True)
    shoulderDystocia = fields.Boolean(required=False, allow_none=True)
    boneFracture = fields.Boolean(required=False, allow_none=True)
    nervePalsy = fields.Boolean(required=False, allow_none=True)
    respiratoryDistressSyndrome = fields.Boolean(required=False, allow_none=True)
    neonatal_complications_other = fields.String(
        required=False,
        allow_none=True,
    )
    feeding_method = fields.String(
        required=False,
        allow_none=True,
    )

    apgar_1_minute = fields.Integer(
        required=False,
        allow_none=True,
    )
    apgar_5_minute = fields.Integer(
        required=False,
        allow_none=True,
    )
