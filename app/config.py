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

from functools import lru_cache
from typing import Any
from typing import Dict
from typing import Optional

from common import VaultClient
from pydantic import BaseSettings
from pydantic import Extra


class VaultConfig(BaseSettings):
    """Store vault related configuration."""

    APP_NAME: str = 'bff-cli'
    CONFIG_CENTER_ENABLED: bool = False

    VAULT_URL: Optional[str]
    VAULT_CRT: Optional[str]
    VAULT_TOKEN: Optional[str]

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    config = VaultConfig()

    if not config.CONFIG_CENTER_ENABLED:
        return {}

    client = VaultClient(
        config.VAULT_URL,
        config.VAULT_CRT,
        config.VAULT_TOKEN)
    return client.get_from_vault(config.APP_NAME)


class Settings(BaseSettings):
    version = '1.7.0'
    port: int = 5080
    host: str = '0.0.0.0'
    RDS_PWD: str
    CLI_SECRET: str = ''
    OPEN_TELEMETRY_HOST: str = '0.0.0.0'
    OPEN_TELEMETRY_PORT: int = 6831
    OPEN_TELEMETRY_ENABLED: str = 'True'
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
    RDS_DB_URI: str
    METADATA_SERVICE: str

    def __init__(self):
        super().__init__()
        self.RDS_DB_URI = self.RDS_DB_URI.replace(
            'postgresql', 'postgresql+asyncpg'
        )

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
    settings = Settings()
    return settings


ConfigClass = get_settings()
