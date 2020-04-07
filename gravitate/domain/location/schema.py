from flask_boiler import schema, fields


class UserLocationFormSchema(schema.Schema):
    user_location = fields.Raw(
        missing=fields.allow_missing, load_only=True, required=False)
    place_id = fields.Raw()
    user_id = fields.Raw(dump_only=True)
    latitude = fields.Raw()
    longitude = fields.Raw()
    address = fields.Raw()


class UserSublocationFormSchema(schema.Schema):

    user_location = fields.Raw(
        missing=fields.allow_missing, load_only=True, required=False)
    location = fields.Raw(
        missing=fields.allow_missing, load_only=True, required=False)

    place_id = fields.Raw()
    user_id = fields.Raw()
    latitude = fields.Raw()
    longitude = fields.Raw()
    address = fields.Raw()
