from pydantic import Field, BaseModel
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
    """
    KG Resource Response Class
    """
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
                    'feedback': 'Resource http://sample-url/kg/v1/resources/pilot/CORE_Datasets/_/1634922993 already exists in project pilot/CORE_Datasets'
                    }
                    }
                }
            }
    )
