from marshmallow import Schema, fields, validate, post_load
from datetime import date
from flask_login import current_user

from src.constants import MIN_LEND_DURATION, MAX_LEND_DURATION


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


class AddNewBookSchema(Schema):
    title = fields.Str(data_key='title', required=True, validate=validate.Length(min=2, max=70))
    author = fields.Str(data_key='author', required=True, validate=validate.Length(min=2, max=30))
    description = fields.Str(data_key='description', allow_none=True)
    image_url = fields.URL(data_key='imageUrl', load_only=True)

    @post_load
    def add_owner_id(self, data, **kwargs):
        data['owner_id'] = current_user.id
        return data


# USER SCHEMAS
class UserPublicSchema(Schema):
    id = fields.Int(data_key='id')
    first_name = fields.Str(data_key='firstName', required=True)
    email = fields.Email(data_key='email', required=True, load_only=True)
    duration = fields.Int(data_key='duration', validate=validate.Range(min=MIN_LEND_DURATION, max=MAX_LEND_DURATION))


class UserRegisterSchema(Schema):
    first_name = fields.Str(data_key='firstName', required=True)
    last_name = fields.Str(data_key='lastName', required=True)
    email = fields.Email(data_key='email', required=True, load_only=True)
    password = fields.Str(data_key='password', required=True, load_only=True)


class UserLoginSchema(Schema):
    email = fields.Email(data_key='email', required=True)
    password = fields.Str(data_key='password', required=True, load_only=True)

