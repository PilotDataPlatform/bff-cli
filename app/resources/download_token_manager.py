import jwt
from .error_handler import customized_error_template, ECustomizedError
from ..config import ConfigClass


def verify_download_token(token):
    '''
    verify download token with the download key
    '''
    try:
        res = jwt.decode(token, ConfigClass.DOWNLOAD_KEY,
                         algorithms=['HS256'])
        for param in ["full_path"]:
            if not param in res:
                # forged token probably
                return False, customized_error_template(ECustomizedError.FORGED_TOKEN)
        return True, res
    except jwt.ExpiredSignatureError:
        return False, customized_error_template(ECustomizedError.TOKEN_EXPIRED)
    except Exception as e:
        return False, customized_error_template(ECustomizedError.INVALID_TOKEN) % str(e)


def generate_token(payload: dict):
    '''
    generate jwt token with the download key
    '''
    return jwt.encode(payload, key=ConfigClass.DOWNLOAD_KEY,
                      algorithm='HS256').decode('utf-8')
