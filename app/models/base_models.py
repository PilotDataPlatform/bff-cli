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

from enum import Enum

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class EAPIResponseCode(Enum):
    success = 200
    internal_error = 500
    bad_request = 400
    not_found = 404
    forbidden = 403
    unauthorized = 401
    conflict = 409


class APIResponse(BaseModel):
    code: EAPIResponseCode = EAPIResponseCode.success
    error_msg: str = ''
    result = []

    def json_response(self):
        data = self.dict()
        data['code'] = self.code.value
        return JSONResponse(status_code=self.code.value, content=data)
