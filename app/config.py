import os
import requests
from requests.models import HTTPError
from pydantic import BaseSettings, Extra
from typing import Dict, Set, List, Any
from functools import lru_cache
from pprint import pprint

SRV_NAMESPACE = os.environ.get("APP_NAME", "bff_vrecli")
CONFIG_CENTER_ENABLED = os.environ.get("CONFIG_CENTER_ENABLED", "false")
CONFIG_CENTER_BASE_URL = os.environ.get("CONFIG_CENTER_BASE_URL", "NOT_SET")
print(f"CONFIG_CENTER_ENABLED {CONFIG_CENTER_ENABLED}")

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
    port: int = 5065
    host: str = "0.0.0.0"
    

    # the packaged modules
    API_MODULES: List = ["bff_vrecli"]
    if not CONFIG_CENTER_ENABLED:
        NEO4J_SERVICE: str
        FILEINFO_HOST: str 
        AUTH_SERVICE :str 
        UPLOAD_VRE: str 
        UPLOAD_GREENROOM: str 
        COMMON_SERVICE: str 
        PROVENANCE_SERVICE: str
        HPC_SERVICE: str 
        RDS_HOST: str
        RDS_PORT: str
        RDS_DBNAME: str
        RDS_USER: str 
        RDS_PWD: str 
        RDS_SCHEMA_DEFAULT:str
        CLI_SECRET: str = ""
    else:
        settings = vault_factory(CONFIG_CENTER_BASE_URL)
        NEO4J_SERVICE: str = settings.get('NEO4J_SERVICE') 
        NEO4J_SERVICE_v2: str = settings.get('NEO4J_SERVICE_v2')
        FILEINFO_HOST: str = settings.get('FILEINFO_HOST')
        AUTH_SERVICE :str = settings.get('AUTH_SERVICE')
        UPLOAD_VRE: str = settings.get('UPLOAD_VRE')
        UPLOAD_GREENROOM: str = settings.get('UPLOAD_GREENROOM')
        COMMON_SERVICE: str = settings.get('UTILITY_SERVICE')
        PROVENANCE_SERVICE: str  = settings.get('PROVENANCE_SERVICE')
        HPC_SERVICE: str  = settings.get('HPC_SERVICE')
        RDS_HOST: str = settings.get('RDS_HOST')
        RDS_PORT: str = settings.get('RDS_PORT')
        RDS_DBNAME: str = settings.get('RDS_DBNAME')
        RDS_USER: str  = settings.get('RDS_USER')
        RDS_PWD: str  = settings.get('RDS_PWD')
        RDS_SCHEMA_DEFAULT:str = settings.get('RDS_SCHEMA_DEFAULT')
        CLI_SECRET: str = settings.get('CLI_SECRET')


    class Config:
        env_file_encoding = 'utf-8'

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
    print(CONFIG_CENTER_ENABLED)
    settings =  Settings()
    pprint(settings)
    return settings

class ConfigClass(object):
    settings = get_settings()
    version = "1.6.0"
    NEO4J_SERVICE = settings.NEO4J_SERVICE
    FILEINFO_HOST = settings.FILEINFO_HOST
    AUTH_SERVICE = settings.AUTH_SERVICE
    UPLOAD_VRE = settings.UPLOAD_VRE
    UPLOAD_GREENROOM = settings.UPLOAD_GREENROOM
    COMMON_SERVICE = settings.COMMON_SERVICE
    PROVENANCE_SERVICE = settings.PROVENANCE_SERVICE
    HPC_SERVICE = settings.HPC_SERVICE
    RDS_HOST = settings.RDS_HOST
    RDS_PORT = settings.RDS_PORT
    RDS_DBNAME = settings.RDS_DBNAME
    RDS_USER = settings.RDS_USER
    RDS_PWD = settings.RDS_PWD
    RDS_SCHEMA_DEFAULT = settings.RDS_SCHEMA_DEFAULT
    SQLALCHEMY_DATABASE_URI = f"postgres://{RDS_USER}:{RDS_PWD}@{RDS_HOST}/{RDS_DBNAME}"
    CLI_SECRET = settings.CLI_SECRET
