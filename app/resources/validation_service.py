from ..resources. error_handler import customized_error_template, ECustomizedError
from ..models.base_models import APIResponse, EAPIResponseCode
from ..models.error_model import InvalidEncryptionError
from .database_service import RDConnection
from .helpers import *
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64

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
        key = base64.urlsafe_b64encode(kdf.derive('SECRETKEYPASSWORD'.encode()))
        f = Fernet(key)
        decrypted = f.decrypt(base64.b64decode(encrypted_message))
        return decrypted.decode()
    except Exception as e:
        raise InvalidEncryptionError("Invalid encryption, could not decrypt message")

class ManifestValidator:

    def __init__(self):
        self.db = RDConnection()

    @staticmethod
    def validate_has_non_optional_attribute_field(input_attributes, compare_attr):
        if not compare_attr.get('optional') and not compare_attr.get('name') in input_attributes:
            return customized_error_template(ECustomizedError.MISSING_REQUIRED_ATTRIBUTES)

    @staticmethod
    def validate_attribute_field_by_value(input_attributes, compare_attr):
        attr_name = compare_attr.get('name')
        value = input_attributes.get(attr_name)
        if value and compare_attr.get('type') == "text":
            if len(value) > 100:
                return customized_error_template(ECustomizedError.TEXT_TOO_LONG) % attr_name
        elif value and compare_attr.get('type') == 'multiple_choice':
            if value not in compare_attr.get('value').split(","):
                return customized_error_template(ECustomizedError.INVALID_CHOICE) % attr_name
        else:
            if not compare_attr.get('optional'):
                return customized_error_template(ECustomizedError.FIELD_REQUIRED) % attr_name

    @staticmethod
    def validate_attribute_name(input_attributes, exist_attributes):
        valid_attributes = [attr.get('name') for attr in exist_attributes]
        for key, value in input_attributes.items():
            if key not in valid_attributes:
                return customized_error_template(ECustomizedError.INVALID_ATTRIBUTE) % key

    def has_valid_attributes(self, event):
        attributes = event.get('attributes')
        exist_attributes = self.db.get_attributes_in_manifest_in_db(event)
        _name_error = self.validate_attribute_name(attributes, exist_attributes)
        if _name_error:
            return _name_error
        for attr in exist_attributes:
            required_attr = attr.get('name')
            if not attr.get('optional') and required_attr not in attributes:
                return customized_error_template(ECustomizedError.MISSING_REQUIRED_ATTRIBUTES) % required_attr
            elif attr not in exist_attributes:
                return customized_error_template(ECustomizedError.INVALID_ATTRIBUTE) % attr
            else:
                _optional_error = self.validate_has_non_optional_attribute_field(attributes, attr)
                if _optional_error:
                    return _optional_error
                _value_error = self.validate_attribute_field_by_value(attributes, attr)
                if _value_error:
                    return _value_error