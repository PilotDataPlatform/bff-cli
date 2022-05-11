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

from pydantic import Field

from .base_models import APIResponse


class CheckFileResponse(APIResponse):
    result: dict = Field({}, example={
        'id': 2077,
        'labels': [
            'File',
            'Greenroom'
            'Raw'
        ],
        'global_entity_id': 'file_data-2a7ea1d8-7dea-11eb-8428-be498ca98c54',
        'operator': '',
        'file_size': 1048576,
        'tags': [],
        'archived': 'false',
        'path': '/data/core-storage/project/raw',
        'time_lastmodified': '2021-03-05T19:37:06',
        'uploader': 'admin',
        'process_pipeline': '',
        'name': 'Testdateiäöüßs4',
        'time_created': '2021-03-05T19:37:06',
        'guid': 'f91b258d-2f1d-409a-9551-91af8057e70e',
        'full_path': '/data/core-storage/project/raw/Testdateiäöüßs4',
        'dcm_id': 'undefined'
    }
    )
