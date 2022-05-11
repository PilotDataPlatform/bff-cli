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


class ProjectListResponse(APIResponse):
    """Project list response class."""
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'result': [
            {
                'name': 'Sample project 1',
                'code': 'sampleproject1'
            },
            {
                'name': 'Sample Project 2',
                'code': 'sampleproject2'
            }
        ]
    }
    )


class POSTProjectFileResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'result': {}
    }
    )


class POSTProjectFile(BaseModel):
    operator: str
    job_type: str
    upload_message: str
    type: str
    zone: str
    filename: str
    dcm_id: str
    current_folder_node: str
    data: list


class GetProjectRoleResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'result': 'role'
    }
    )


class GetProjectFolder(BaseModel):
    project_code: str
    zone: str
    folder: str
    relative_path: str


class GetProjectFolderResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'result': {
            'id': 1552,
            'labels': [
                'Greenroom',
                'Folder'
            ],
            'global_entity_id': 'bc8b4239-b22a-47dd-9d23-36ade331ebbf',
            'folder_level': 1,
            'list_priority': 10,
            'folder_relative_path': 'cli_folder_test23',
            'time_lastmodified': '2021-05-10T22:18:29',
            'uploader': 'admin',
            'name': 'folder_test',
            'time_created': '2021-05-10T22:18:29',
            'project_code': 'sampleproject',
            'tags': []
        }
    }
    )
