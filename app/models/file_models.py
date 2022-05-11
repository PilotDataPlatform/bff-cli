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


class GetProjectFileList(BaseModel):
    project_code: str
    zone: str
    folder: str
    source_type: str


class GetProjectFileListResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'result': [
            {
                'id': 6127,
                'labels': [
                    'File',
                    'Greenroom'
                ],
                'global_entity_id': 'baee1ca0-37a5-4c9b-afcb-1b2d4b2447aa',
                'project_code': 'sampleproject',
                'operator': 'admin',
                'file_size': 1048576,
                'tags': [],
                'list_priority': 20,
                'archived': 'false',
                'path': '/data/core-storage/sampleproject/raw/folders1',
                'time_lastmodified': '2021-05-18T14:34:21',
                'process_pipeline': '',
                'uploader': 'admin',
                'parent_folder_geid': 'c1c3766f-36bd-42db-8ca5-9040726cbc03',
                'name': 'Testdateiäöüßs2',
                'time_created': '2021-05-18T14:34:21',
                'guid': '4e06b8c5-8235-476e-b818-1ea5b0f0043c',
                'full_path': '/data/core-storage/sampleproject/...',
                'dcm_id': 'undefined'
            },
            {
                'id': 2842,
                'labels': [
                    'Greenroom',
                    'Folder'
                ],
                'folder_level': 1,
                'global_entity_id': '7a71ed22-9cd0-465e-a18e-b66fda2c4e04',
                'list_priority': 10,
                'folder_relative_path': 'folders1',
                'time_lastmodified': '2021-05-11T20:17:51',
                'uploader': 'admin',
                'name': 'folders',
                'time_created': '2021-05-11T20:17:51',
                'project_code': 'sampleproject',
                'tags': []
            }
        ]
    }
    )


class POSTDownloadFile(BaseModel):
    files: list
    operator: str
    project_code: str
    session_id: str
    zone: str


class POSTDownloadFileResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'result': {
            'session_id': 'downloadtest',
            'job_id': 'data-download-1621521355',
            'geid': '6c890078-1596-44a5-b695-1a9a1b1d974a-1621347776',
            'source': '/data/core-storage/sampleproject/...',
            'action': 'data_download',
            'status': 'READY_FOR_DOWNLOADING',
            'project_code': 'sampleproject',
            'operator': 'admin',
            'progress': 0,
            'payload': {
                'hash_code': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'files': [
                    '/data/core-storage/sampleproject/raw/contributor_file_a'
                ],
                'zone': 'Greenroom',
                'frontend_zone': 'Green Room'
            },
            'update_timestamp': '1621521356'
        }
    })


class QueryDataInfo(BaseModel):
    geid: list


class QueryDataInfoResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'result': [
            {
                'status': 'Permission Denied',
                'result': [],
                'geid': '2b60f036-9642-44e7-883b-c8ed247b1152'
            },
            {
                'status': 'success',
                'result': [
                    {
                        'id': 23279,
                        'labels': ['Greenroom', 'File'],
                        'global_entity_id': '3586fa29-4a68-b833-...',
                        'display_path': 'admin/Testdateiäöüßs14',
                        'project_code': 'sampleproject',
                        'version_id': '08cac0b1-75cf-4c2e-8bed-c43fa99d682f',
                        'operator': 'admin',
                        'file_size': 1048576,
                        'tags': [],
                        'archived': False,
                        'list_priority': 20,
                        'path': '/data/core-storage/sampleproject/admin',
                        'time_lastmodified': '2021-07-29T18:18:00',
                        'process_pipeline': '',
                        'uploader': 'admin',
                        'parent_folder_geid':'22508bda-4a76-...',
                        'name': 'Testdateiäöüßs14',
                        'time_created':'2021-07-29T18:18:00',
                        'guid': '12e23fb5-51d5-4ee9-8fb4-78fe9f9810d9',
                        'location': 'minio://http://minio.minio:...',
                        'full_path': '/data/core-storage/sampleproject/...',
                        'dcm_id': 'undefined'
                    }
                ],
                'geid': '3586fa29-18ef-4a68-b833-5c04d3c2831c'
            },
            {
                'status': 'Permission Denied',
                'result': [],
                'geid': 'a17fcf3a-179c-4099-a607-1438464527e2'
            },
            {
                'status': 'File Not Exist',
                'result': [],
                'geid': '80c08693-9ac8-4b94-bb02-9aebe0ec9f20'
            }
        ]}
    )
