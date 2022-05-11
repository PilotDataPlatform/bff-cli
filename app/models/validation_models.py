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


class ManifestValidatePost(BaseModel):
    """Validate Manifest post model."""
    manifest_json: dict = Field({}, example={
        'manifest_name': 'Manifest1',
        'project_code': 'sampleproject',
        'attributes': {'attr1': 'a1', 'attr2': 'test cli upload'},
        'file_path': '/data/core-storage/sampleproject/raw/testf1'
    }
    )


class ManifestValidateResponse(APIResponse):
    """Validate Manifest Response class."""
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'result': 'Valid'
    }
    )


class ValidateDICOMIDPOST(BaseModel):
    """Validate DICOM ID Post model."""
    dcm_id: str


class ValidateDICOMIDResponse(APIResponse):
    """Validate DICOM ID response class."""
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'result': 'VALID'
    }
    )


class EnvValidatePost(BaseModel):
    """Validate Environment post model."""
    action: str
    environ: str
    zone: str


class EnvValidateResponse(APIResponse):
    """Validate Manifest Response class."""
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'result': 'valid'
    }
    )
