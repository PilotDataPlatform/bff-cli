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
    INTERNAL = "INTERNAL"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    MANIFEST_NOT_FOUND = "MANIFEST_NOT_FOUND"
    INVALID_ATTRIBUTE = "INVALID_ATTRIBUTE"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    MISSING_REQUIRED_ATTRIBUTES = "MISSING_REQUIRED_ATTRIBUTES"
    INVALID_CHOICE = "INVALID_CHOICE"
    FIELD_REQUIRED = "FIELD_REQUIRED"
    TEXT_TOO_LONG = "TEXT_TOO_LONG"
    INVALID_GENERATE_ID = "INVALID_GENERATE_ID"
    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"


def customized_error_template(customized_error: ECustomizedError):
    '''
    get error template
    '''
    return {
        "INTERNAL": "[Internal] %s",
        "FILE_NOT_FOUND": "File Not Exist",
        "MANIFEST_NOT_FOUND": "Manifest Not Exist %s",
        "INVALID_ATTRIBUTE": "Invalid Attribute %s",
        "TOKEN_EXPIRED": "Token Expired",
        "MISSING_REQUIRED_ATTRIBUTES": "Missing Required Attribute %s",
        "INVALID_CHOICE": "Invalid Choice Field %s",
        "FIELD_REQUIRED": "Field Required %s",
        "TEXT_TOO_LONG": "Text Too Long %s",
        "INVALID_GENERATE_ID": "Invalid Generate ID",
        "PROJECT_NOT_FOUND": "Project not found"
    }.get(
        customized_error.name, "Unknown Error"
    )
