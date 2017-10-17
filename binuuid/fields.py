import uuid

from django.core import exceptions
from django.db import models
from django.utils.translation import ugettext_lazy as _


def generate_db_uuid():
    return uuid.UUID(int=_optimize_bytes(uuid.uuid1().int))
 
 
def _optimize_bytes(value):
    return (
        ((value & 0x000000000000FFFF0000000000000000) << 48) |
        ((value & 0x00000000FFFF00000000000000000000) << 16) |
        ((value & 0xFFFFFFFF000000000000000000000000) >> 32) |
        ((value & 0x0000000000000000FFFFFFFFFFFFFFFF)))


class BinaryUUIDField(models.Field):
    """
    A UUID field type backed with binary storage, and an index-optimized
    binary represenation for a sensible default.
    """

    default_error_messages = {
        'invalid': _("'%(value)s' is not a valid UUID."),
    }
    description = 'Universally unique identifier'
    empty_strings_allowed = False

    def __init__(self, verbose_name=None, default=generate_db_uuid, **kwargs):
        kwargs['max_length'] = 32
        super(UUIDField, self).__init__(verbose_name, default, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(BinaryUUIDField, self).deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs

    def db_type(self, connection):
        if connection.vendor != 'mysql':
            raise NotImplemented('This field only supports MySQL at this time.')
        return 'binary(16)'

    def rel_db_type(self, connection):
        return self.db_type(connection)

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        if not isinstance(value, uuid.UUID):
            value = self.to_python(value)
        return value.bytes
    
    def from_db_value(self, value):
        return self.to_python(value)

    def to_python(self, value):
        if value is not None and not isinstance(value, uuid.UUID):
            try:
                if isinstance(value, bytes):
                    return uuid.UUID(bytes=value)
                if isinstance(value, int):
                    return uuid.UUID(int=value)
                return uuid.UUID(value)
            except (AttributeError, ValueError):
                raise exceptions.ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': value},
                )
        return value

    def value_to_string(self, obj):
        return self.value_from_object(obj).hex

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.UUIDField,
        }
        defaults.update(kwargs)
        return super(BinaryUUIDField, self).formfield(**defaults)



