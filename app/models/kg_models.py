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


class KGImportPost(BaseModel):
    data: dict = Field({}, example={
        'dataset_code': [],
        'data': {
            'kg_cli_test1_1634922993.json': {
                '@id': '1634922993',
                '@type': 'unit test',
                'key_value_pairs': {
                    'definition_file': True,
                    'file_type': 'KG unit test',
                    'existing_duplicate': False
                }
            }
        }
    }
    )


class KGResponseModel(APIResponse):
    """KG Resource Response Class."""
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'result': {
            'processing': {},
            'ignored': {
                'kg_cli_test1_1634922993.json': {
                    '@id': '1634922993',
                    '@type': 'unit test',
                    'key_value_pairs': {
                        'definition_file': True,
                        'file_type': 'KG unit test',
                        'existing_duplicate': False
                    },
                    '@context': 'https://context.org',
                    'feedback': 'Resource http://sample-url/kg/v1/... \
                        already exists in project pilot/CORE_Datasets'
                }
            }
        }
    }
    )
