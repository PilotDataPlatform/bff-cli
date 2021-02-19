import enum
from ..models.base_models import APIResponse, EAPIResponseCode
from functools import wraps


def catch_internal(api_namespace):
    '''
    decorator to catch internal server error.
    '''
    def decorator(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as exce:
                respon = APIResponse()
                respon.code = EAPIResponseCode.internal_error
                respon.result = None
                err = api_namespace + " " + str(exce)
                respon.error_msg = customized_error_template(
                    ECustomizedError.INTERNAL) % err
                return respon.json_response()
        return inner
    return decorator


class ECustomizedError(enum.Enum):
    '''
    Enum of customized errors
    '''
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    MANIFEST_NOT_FOUND = "MANIFEST_NOT_FOUND"
    INVALID_ATTRIBUTE = "INVALID_ATTRIBUTE"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    REGEX_VALIDATION_ERROR = "REGEX_VALIDATION_ERROR"
    MISSING_REQUIRED_ATTRIBUTES = "MISSING_REQUIRED_ATTRIBUTES"
    INVALID_CHOICE = "INVALID_CHOICE"
    FIELD_REQUIRED = "FIELD_REQUIRED"
    TEXT_TOO_LONG = "TEXT_TOO_LONG"
    INVALID_GENERATE_ID = "INVALID_GENERATE_ID"


def customized_error_template(customized_error: ECustomizedError):
    '''
    get error template
    '''
    return {
        "FILE_NOT_FOUND": "File Not Exist",
        "MANIFEST_NOT_FOUND": "Manifest Not Exist",
        "INVALID_ATTRIBUTE": "Invalid Attribute",
        "TOKEN_EXPIRED": "Token Expired",
        "REGEX_VALIDATION_ERROR": "Regex Validation Error",
        "MISSING_REQUIRED_ATTRIBUTES": "Missing Required Attribute",
        "INVALID_CHOICE": "Invalid Choice Field",
        "FIELD_REQUIRED": "Field Required",
        "TEXT_TOO_LONG": "Text Too Long",
        "INVALID_GENERATE_ID": "Invalid Generate ID"
    }.get(
        customized_error.name, "Unknown Error"
    )
