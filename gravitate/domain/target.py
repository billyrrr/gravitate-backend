from flask_boiler import schema, fields, domain_model


class TargetSchema(schema.Schema):

    earliest_arrival = fields.Integer()
    latest_arrival = fields.Integer()
    earliest_departure = fields.Integer()
    latest_departure = fields.Integer()
    r_ref = fields.Relationship(nested=False)
    from_lat = fields.Raw()
    from_lng = fields.Raw()
    to_lat = fields.Raw()
    to_lng = fields.Raw()


class Target(domain_model.DomainModel):

    class Meta:
        schema_cls = TargetSchema
