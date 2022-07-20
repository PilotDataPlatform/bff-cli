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

from fastapi import FastAPI
from fastapi_health import health

from .routers import api_root
from .routers.v1 import api_dataset
from .routers.v1 import api_file
from .routers.v1 import api_hpc
from .routers.v1 import api_kg
from .routers.v1 import api_lineage
from .routers.v1 import api_manifest
from .routers.v1 import api_project
from .routers.v1 import api_validation
from app.resources.health_check import redis_check


def api_registry(app: FastAPI):
    prefix = '/v1'
    app.add_api_route("/v1/health", health([redis_check], success_status=204, failure_status=503), tags=['Health'])
    app.include_router(api_root.router)
    app.include_router(api_project.router, prefix=prefix)
    app.include_router(api_manifest.router, prefix=prefix)
    app.include_router(api_validation.router, prefix=prefix)
    app.include_router(api_lineage.router, prefix=prefix)
    app.include_router(api_file.router, prefix=prefix)
    app.include_router(api_dataset.router, prefix=prefix)
    app.include_router(api_hpc.router, prefix=prefix)
    app.include_router(api_kg.router, prefix=prefix)
