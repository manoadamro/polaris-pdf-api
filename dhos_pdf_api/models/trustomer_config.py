from marshmallow import Schema, fields

# These schemas are not exhaustive, containing only a subset of the information
# required to generate a SEND PDF.


class EscalationPolicy(Schema):
    routine_monitoring = fields.String(required=True)
    low_monitoring = fields.String(required=True)
    low_medium_monitoring = fields.String(required=True)
    medium_monitoring = fields.String(required=True)
    high_monitoring = fields.String(required=True)


class OxygenMaskConfigSchema(Schema):
    code = fields.String(required=True)
    name = fields.String(required=True)


class News2ConfigSchema(Schema):
    zero_severity_interval_hours = fields.Number(required=True)
    low_severity_interval_hours = fields.Number(required=True)
    low_medium_severity_interval_hours = fields.Number(required=True)
    medium_severity_interval_hours = fields.Number(required=True)
    high_severity_interval_hours = fields.Number(required=True)
    escalation_policy = fields.Nested(EscalationPolicy(), required=True)


class SendConfigSchema(Schema):
    news2 = fields.Nested(News2ConfigSchema, required=True)
    oxygen_masks = fields.List(fields.Nested(OxygenMaskConfigSchema()), required=True)


class TrustomerConfigSchema(Schema):
    send_config = fields.Nested(SendConfigSchema, required=True)
