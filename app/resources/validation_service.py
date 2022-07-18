# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import base64

from common import LoggerFactory
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..models.error_model import InvalidEncryptionError
from ..models.error_model import ValidationError
from ..resources.error_handler import ECustomizedError
from ..resources.error_handler import customized_error_template

_logger = LoggerFactory('validation_service').get_logger()


def decryption(encrypted_message, secret):
    """
    decrypt byte that encrypted by encryption function
    encrypted_message: the string that need to decrypt to string
    secret: the string type secret key used to encrypt message
    return: string of the message
    """
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=base64.b64decode(secret),
            iterations=100000,
            backend=default_backend()
        )
        # use the key from current device information
        key = base64.urlsafe_b64encode(
            kdf.derive('SECRETKEYPASSWORD'.encode()))
        f = Fernet(key)
        decrypted = f.decrypt(base64.b64decode(encrypted_message))
        return decrypted.decode()
    except Exception:
        raise InvalidEncryptionError(
            'Invalid encryption, could not decrypt message'
        )


class ManifestValidator:

    def __init__(self, current_attribute, target_attribute):
        self.current_attribute = current_attribute
        self.target_attribute = target_attribute

    def validate_attributes_name(self):
        _logger.info('validate_attributes_name'.center(80, '-'))
        allowed_attributes = [attr.get('name') for attr in self.target_attribute]
        for attr in self.current_attribute.keys():
            if attr not in allowed_attributes:
                error = f'invalid attribute {attr}'
                _logger.error(f'Error attribute field: {error}')
                raise ValidationError(error)

    def validate_non_optional_attribute_field(self, attr):
        _logger.info('validate_non_optional_attribute_field'.center(80, '-'))
        required_attr = attr.get('name')
        if not attr.get('optional') and required_attr not in self.current_attribute.keys():
            error = customized_error_template(ECustomizedError.FIELD_REQUIRED) % required_attr
            _logger.error(f'Error attribute field: {error}')
            raise ValidationError(error)
        elif not self.current_attribute.get(required_attr):
            error = customized_error_template(ECustomizedError.MISSING_REQUIRED_ATTRIBUTES) % required_attr
            _logger.error(f'Error attribute field: {error}')
            raise ValidationError(error)

    def validate_attribute_value(self, attr):
        _logger.info('validate_attribute_value'.center(80, '-'))
        attr_name = attr.get('name')
        current_attr = self.current_attribute.get(attr_name)
        if not current_attr:
            error = f'Invalid attr: {attr}'
            _logger.error(f'Error attribute field: {error}')
            raise ValidationError(error)
        attr_name = attr.get('name')
        exceed_length = len(current_attr) > 100
        valid_choice = attr.get('options')
        if attr.get('type') == 'text' and exceed_length:
            error = customized_error_template(ECustomizedError.TEXT_TOO_LONG) % attr_name
            _logger.error(f'Error attribute field: {error}')
            raise ValidationError(error)
        elif attr.get('type') == 'multiple_choice' and current_attr not in valid_choice:
            error = customized_error_template(ECustomizedError.INVALID_CHOICE) % attr_name
            _logger.error(f'Error attribute field: {error}')
            raise ValidationError(error)

    async def has_valid_attributes(self):
        _logger.info('has_valid_attributes'.center(80, '-'))
        try:
            self.validate_attributes_name()
            for attr in self.target_attribute:
                self.validate_non_optional_attribute_field(attr)
                self.validate_attribute_value(attr)
        except ValidationError as e:
            _logger.error(e.error_msg)
            return e.error_msg
