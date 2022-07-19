from marshmallow import EXCLUDE, Schema, fields

# These schemas are not exhaustive, containing only a sanity check of the information
# required to generate a SEND PDF.


class PatientSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    dob = fields.String(required=False, allow_none=True)
    hospital_number = fields.String(required=True)
    nhs_number = fields.String(required=False, allow_none=True)
    sex = fields.String(required=False, allow_none=True)


class ClinicianSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    uuid = fields.String(required=True)


class ScoreSystemHistorySchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    score_system = fields.String(required=False, allow_none=True)
    spo2_scale = fields.Integer(required=False, allow_none=True)
    changed_by = fields.Nested(ClinicianSchema)
    changed_time = fields.String()


class EncounterSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    uuid = fields.String(required=True)
    created = fields.String(required=True, allow_none=False)
    admitted_at = fields.String(required=True)
    discharged_at = fields.String(required=False, allow_none=True)
    epr_encounter_id = fields.String(required=False, allow_none=True)
    spo2_scale = fields.Integer(required=False, allow_none=True)
    score_system_history = fields.List(
        fields.Nested(ScoreSystemHistorySchema), required=False
    )


class ObservationSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    measured_time = fields.String(required=True)
    observation_metadata = fields.Dict(required=False, allow_none=True)
    observation_string = fields.String(required=False, allow_none=True)
    observation_type = fields.String(required=True)
    observation_unit = fields.String(required=False, allow_none=True)
    observation_value = fields.Number(required=False, allow_none=True)
    patient_refused = fields.Boolean(required=False, allow_none=True)
    score_value = fields.Integer(required=False, allow_none=True)
    uuid = fields.String(required=False, allow_none=True)


class ObservationSetSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    created_by = fields.Dict(required=True, allow_none=True)
    is_partial = fields.Boolean(required=False, allow_none=True)
    observations = fields.List(fields.Nested(ObservationSchema), required=True)
    record_time = fields.String(required=True)
    score_severity = fields.String(required=True, allow_none=True)
    score_string = fields.String(required=True, allow_none=True)
    score_system = fields.String(required=True)
    score_value = fields.Integer(required=True, allow_none=True)
    spo2_scale = fields.Integer(required=True)


class MetricSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    metric_name = fields.String(
        metadata={"example": "count_obs_sets_on_time_high_risk"}
    )
    metric_date = fields.String(metadata={"example": "2019-08-01"})
    metric_value = fields.Integer(metadata={"example": 123})
    measurement_timestamp = fields.String(
        metadata={"example": "2019-08-01T00:09:00.000"}
    )
