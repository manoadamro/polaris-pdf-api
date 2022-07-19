from marshmallow import EXCLUDE, Schema, fields


class PersonalAddressSchema(Schema):
    class Meta:
        title = "Patient personal address"
        unknown = EXCLUDE
        ordered = True

    postcode = fields.Field(required=False, allow_none=True)


class PatientSchema(Schema):
    class Meta:
        title = "Full patient schema"
        unknown = EXCLUDE
        ordered = True

    uuid = fields.String(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    hospital_number = fields.String(required=True)
    nhs_number = fields.String(required=False, allow_none=True)

    status = fields.Field(required=False, allow_none=True)
    dob = fields.String(required=False, allow_none=True)
    bmi = fields.Field(required=False, allow_none=True)
    diabetes_type = fields.Field(required=False, allow_none=True)
    allowed_to_text = fields.Boolean(required=False, allow_none=True)
    allowed_to_email = fields.Boolean(required=False, allow_none=True)
    phone_number = fields.String(required=False, allow_none=True)
    email_address = fields.String(required=False, allow_none=True)
    personal_address = fields.Nested(
        PersonalAddressSchema, required=False, allow_none=True
    )
    accessibility_considerations = fields.Field(required=False, allow_none=True)
    other_notes = fields.String(required=False, allow_none=True)


class ReadingsPlanSchema(Schema):
    class Meta:
        title = "Patient readings plan"
        unknown = EXCLUDE
        ordered = True

    days_per_week_to_take_readings = fields.Integer(required=False, allow_none=True)
    readings_per_day = fields.Integer(required=False, allow_none=True)


class LatestVisitSchema(Schema):
    class Meta:
        title = "Patient latest visit"
        unknown = EXCLUDE
        ordered = True

    visit_date = fields.String(required=False, allow_none=True)


class ManagementPlan(Schema):
    class Meta:
        title = "Management plan"
        unknown = EXCLUDE
        ordered = True

    management_strategy = fields.Field(required=False, allow_none=True)


class Hba1cSchema(Schema):
    class Meta:
        title = "HbA1c"
        unknown = EXCLUDE
        ordered = True

    value = fields.Field(required=False, allow_none=True)
    date = fields.String(required=False, allow_none=True)


class Diabetes(Schema):
    class Meta:
        title = "Diabetes"
        unknown = EXCLUDE
        ordered = True

    diagnosed = fields.Field(required=False, allow_none=True)
    diagnosis_tool = fields.Field(required=False, allow_none=True)
    risk_factors = fields.Field(required=False, allow_none=True)
    diagnosis_other = fields.Field(required=False, allow_none=True)
    first_hba1c = fields.Nested(Hba1cSchema, required=False, allow_none=True)
    latest_hba1c = fields.Nested(Hba1cSchema, required=False, allow_none=True)


class BloodGlucoseReadingAlert(Schema):
    class Meta:
        title = "Blood glucose reading alert"
        unknown = EXCLUDE
        ordered = True

    dismissed = fields.Boolean(required=False, allow_none=True)


class PrandialTag(Schema):
    class Meta:
        title = "Prandial tag"
        unknown = EXCLUDE
        ordered = True

    description = fields.Field(required=False, allow_none=True)


class Dose(Schema):
    class Meta:
        title = "Dose"
        unknown = EXCLUDE
        ordered = True

    amount = fields.Field(required=False, allow_none=True)
    medication_id = fields.Field(required=False, allow_none=True)


class BloodGlucoseReading(Schema):
    class Meta:
        title = "Blood glucose reading"
        unknown = EXCLUDE
        ordered = True

    alert = fields.Nested(BloodGlucoseReadingAlert, required=False, allow_none=True)
    measured_timestamp = fields.String(required=False, allow_none=True)
    prandial_tag = fields.Nested(PrandialTag, required=False, allow_none=True)
    blood_glucose_value = fields.Field(required=False, allow_none=True)
    units = fields.Field(required=False, allow_none=True)
    doses = fields.List(fields.Nested(Dose), required=False, allow_none=True)
    comment = fields.String(required=False, allow_none=True)
