import os
from dotenv import load_dotenv
from pydantic import BaseSettings, Extra
from typing import Dict, Set, List, Any
from functools import lru_cache
from common import VaultClient

load_dotenv()
SRV_NAMESPACE = os.environ.get("APP_NAME", "bff_cli")
CONFIG_CENTER_ENABLED = os.environ.get("CONFIG_CENTER_ENABLED", "false")


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == 'false':
        return {}
    else:
        vc = VaultClient(os.getenv("VAULT_URL"), os.getenv("VAULT_CRT"), os.getenv("VAULT_TOKEN"))
        return vc.get_from_vault(SRV_NAMESPACE)

class Settings(BaseSettings):
    version = "1.7.0"
    port: int = 5080
    host: str = "0.0.0.0"
    RDS_PWD: str
    CLI_SECRET: str = ''
    OPEN_TELEMETRY_HOST: str = '0.0.0.0'
    OPEN_TELEMETRY_PORT: int = 6831
    OPEN_TELEMETRY_ENABLED: str="True"
    CORE_ZONE_LABEL: str = ''
    GREEN_ZONE_LABEL: str = ''
    AUTH_SERVICE: str 
    DATA_UPLOAD_SERVICE_GREENROOM: str
    DATA_UPLOAD_SERVICE_CORE: str
    FILEINFO_HOST: str
    HPC_SERVICE: str 
    KG_SERVICE: str 
    PROVENANCE_SERVICE: str 
    RDS_HOST: str 
    RDS_DBNAME: str 
    RDS_USER: str 
    RDS_SCHEMA_DEFAULT: str 
    NEO4J_SERVICE: str

    def __init__(self):
        super().__init__()
        self.SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://{self.RDS_USER}:{self.RDS_PWD}@{self.RDS_HOST}/{self.RDS_DBNAME}"


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
                init_settings,
                env_settings,
                load_vault_settings,
                file_secret_settings,
            )

ConfigClass = Settings()
