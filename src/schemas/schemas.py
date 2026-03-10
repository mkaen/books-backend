from marshmallow import Schema, fields, validate
from datetime import date


class BookSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(data_key='title', required=True, validate=validate.Length(min=2, max=70))
    author = fields.Str(data_key='author', required=True, validate=validate.Length(min=2, max=30))
    description = fields.Str(data_key='description', allow_none=True)
    image_url = fields.URL(data_key='imageUrl')
    reserved = fields.Bool(data_key='reserved')
    lent_out = fields.Bool(data_key='lentOut')
    active = fields.Bool(data_key='active')
    return_date = fields.Date(data_key='returnDate', allow_none=True)
    owner_id = fields.Int(data_key='ownerId', required=True)
    lender_id = fields.Int(data_key='lenderId', allow_none=True)

    overdue = fields.Method("is_overdue", data_key='isOverdue', dump_only=True)

    def is_overdue(self, obj) -> bool:
        """Check current date is passing book returning date."""
        if isinstance(obj, dict):
            return_date = obj.get('return_date')
        else:
            return_date = obj.return_date
        return True if return_date and return_date < date.today() else False
