import os
import httpx
from pydantic import BaseSettings, Extra
from typing import Dict, Set, List, Any
from functools import lru_cache
from common import VaultClient
from common.config import ConfigClass as vault_config

SRV_NAMESPACE = os.environ.get("APP_NAME", "bff_vrecli")
CONFIG_CENTER_ENABLED = os.environ.get("CONFIG_CENTER_ENABLED", "false")
CONFIG_CENTER_BASE_URL = os.environ.get("CONFIG_CENTER_BASE_URL", "NOT_SET")


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == 'false':
        return {}
    else:
        VAULT_SERVICE = "https://127.0.0.1:8200/v1/vre/app/config"
        vc = VaultClient(VAULT_SERVICE, vault_config.VAULT_CRT, vault_config.VAULT_TOKEN)

        return vc.get_from_vault(SRV_NAMESPACE)



class Settings(BaseSettings):
    port: int = 5080
    host: str = "0.0.0.0"
    RDS_PWD: str
    CLI_SECRET: str = ''
    OPEN_TELEMETRY_HOST: str = '0.0.0.0'
    OPEN_TELEMETRY_PORT: int = 6831
    OPEN_TELEMETRY_ENABLED: str="True"
    CORE_ZONE_LABEL: str = ''
    GREEN_ZONE_LABEL: str = ''

    AUTH_SERVICE: str = os.environ.get('AUTH_SERVICE')
    DATA_UPLOAD_SERVICE_CORE: str = os.environ.get('DATA_UPLOAD_SERVICE_CORE')
    DATA_UPLOAD_SERVICE_GREENROOM: str = os.environ.get('DATA_UPLOAD_SERVICE_GREENROOM')
    FILEINFO_HOST: str= os.environ.get('FILEINFO_HOST')
    HPC_SERVICE: str = os.environ.get('HPC_SERVICE')
    KG_SERVICE: str = os.environ.get('KG_SERVICE')
    PROVENANCE_SERVICE: str = os.environ.get('PROVENANCE_SERVICE')
    RDS_HOST: str = os.environ.get('RDS_HOST')
    RDS_PORT: str = os.environ.get('RDS_PORT')
    RDS_DBNAME: str = os.environ.get('RDS_DBNAME')
    RDS_USER: str = os.environ.get('RDS_USER')
    RDS_SCHEMA_DEFAULT: str = os.environ.get('RDS_SCHEMA_DEFAULT')
    NEO4J_SERVICE: str = os.environ.get('NEO4J_SERVICE')


    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return load_vault_settings, env_settings, init_settings, file_secret_settings
            
@lru_cache(1)
def get_settings():
    settings =  Settings()
    return settings

class ConfigClass(object):
    settings = get_settings()
    version = "1.8.0"
    OPEN_TELEMETRY_HOST= settings.OPEN_TELEMETRY_HOST
    OPEN_TELEMETRY_PORT= settings.OPEN_TELEMETRY_PORT
    OPEN_TELEMETRY_ENABLED= settings.OPEN_TELEMETRY_ENABLED
    AUTH_SERVICE = settings.AUTH_SERVICE
    CLI_SECRET = settings.CLI_SECRET
    CORE_ZONE_LABEL = settings.CORE_ZONE_LABEL
    DATA_UPLOAD_SERVICE_CORE = settings.DATA_UPLOAD_SERVICE_CORE
    DATA_UPLOAD_SERVICE_GREENROOM = settings.DATA_UPLOAD_SERVICE_GREENROOM
    FILEINFO_HOST= settings.FILEINFO_HOST
    GREEN_ZONE_LABEL = settings.GREEN_ZONE_LABEL
    HPC_SERVICE = settings.HPC_SERVICE
    KG_SERVICE = settings.KG_SERVICE
    opentelemetry_enabled = settings.OPEN_TELEMETRY_ENABLED
    OPEN_TELEMETRY_HOST = settings.OPEN_TELEMETRY_HOST
    OPEN_TELEMETRY_PORT = settings.OPEN_TELEMETRY_PORT
    PROVENANCE_SERVICE = settings.PROVENANCE_SERVICE
    RDS_HOST = settings.RDS_HOST
    # RDS_PORT = settings.RDS_PORT
    RDS_DBNAME = settings.RDS_DBNAME
    RDS_USER = settings.RDS_USER
    RDS_PWD = settings.RDS_PWD
    RDS_SCHEMA_DEFAULT = settings.RDS_SCHEMA_DEFAULT
    SQLALCHEMY_DATABASE_URI = f"postgresql://{RDS_USER}:{RDS_PWD}@{RDS_HOST}/{RDS_DBNAME}"
    NEO4J_SERVICE = settings.NEO4J_SERVICE
