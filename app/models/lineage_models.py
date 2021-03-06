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

from pydantic import BaseModel
from pydantic import Field

from .base_models import APIResponse


class LineageCreatePost(BaseModel):
    project_code: str
    input_id: str
    output_id: str
    input_name: str
    output_name: str
    pipeline_name: str
    description: str


class LineageCreateResponse(APIResponse):
    """Validate Manifest Response class."""
    result: dict = Field({}, example={
        'message': 'Succeed'
    }
    )
