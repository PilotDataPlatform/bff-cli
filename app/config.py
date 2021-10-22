import os
import requests
from requests.models import HTTPError
from pydantic import BaseSettings, Extra
from typing import Dict, Set, List, Any
from functools import lru_cache

SRV_NAMESPACE = os.environ.get("APP_NAME", "bff_vrecli")
CONFIG_CENTER_ENABLED = os.environ.get("CONFIG_CENTER_ENABLED", "false")
CONFIG_CENTER_BASE_URL = os.environ.get("CONFIG_CENTER_BASE_URL", "NOT_SET")

def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == "false":
        return {}
    else:
        return vault_factory(CONFIG_CENTER_BASE_URL)

def vault_factory(config_center) -> dict:
    url = config_center + \
        "/v1/utility/config/{}".format(SRV_NAMESPACE)
    config_center_respon = requests.get(url)
    if config_center_respon.status_code != 200:
        raise HTTPError(config_center_respon.text)
    return config_center_respon.json()['result']

class Settings(BaseSettings):
    port: int = 5080
    host: str = "0.0.0.0"
    RDS_HOST: str
    RDS_PORT: str
    RDS_DBNAME: str = ""
    RDS_USER: str
    RDS_PWD: str
    RDS_SCHEMA_DEFAULT:str 
    CLI_SECRET: str = ""
    NEO4J_SERVICE: str
    FILEINFO_HOST: str 
    AUTH_SERVICE :str 
    DATA_UPLOAD_SERVICE_VRE: str 
    DATA_UPLOAD_SERVICE_GREENROOM: str 
    UTILITY_SERVICE: str 
    PROVENANCE_SERVICE: str
    HPC_SERVICE: str 
    RDS_HOST: str
    RDS_PORT: str
    RDS_DBNAME: str
    RDS_USER: str 
    RDS_PWD: str 
    RDS_SCHEMA_DEFAULT:str
    KG_SERVICE: str


    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                load_vault_settings,
                env_settings,
                init_settings,
                file_secret_settings,
            )

@lru_cache(1)
def get_settings():
    settings =  Settings()
    return settings

class ConfigClass(object):
    settings = get_settings()
    version = "1.1.0"
    RDS_HOST = settings.RDS_HOST
    RDS_PORT = settings.RDS_PORT
    RDS_DBNAME = settings.RDS_DBNAME
    RDS_USER = settings.RDS_USER
    RDS_PWD = settings.RDS_PWD
    RDS_SCHEMA_DEFAULT = settings.RDS_SCHEMA_DEFAULT
    SQLALCHEMY_DATABASE_URI = f"postgresql://{RDS_USER}:{RDS_PWD}@{RDS_HOST}/{RDS_DBNAME}"
    CLI_SECRET = settings.CLI_SECRET
    NEO4J_SERVICE = settings.NEO4J_SERVICE
    FILEINFO_HOST= settings.FILEINFO_HOST
    AUTH_SERVICE = settings.AUTH_SERVICE
    DATA_UPLOAD_SERVICE_VRE = settings.DATA_UPLOAD_SERVICE_VRE
    DATA_UPLOAD_SERVICE_GREENROOM = settings.DATA_UPLOAD_SERVICE_GREENROOM
    UTILITY_SERVICE = settings.UTILITY_SERVICE
    PROVENANCE_SERVICE = settings.PROVENANCE_SERVICE
    HPC_SERVICE = settings.HPC_SERVICE
    RDS_HOST = settings.RDS_HOST
    RDS_PORT = settings.RDS_PORT
    RDS_DBNAME = settings.RDS_DBNAME
    RDS_USER = settings.RDS_USER
    RDS_PWD = settings.RDS_PWD
    RDS_SCHEMA_DEFAULT = settings.RDS_SCHEMA_DEFAULT
    KG_SERVICE = settings.KG_SERVICE
