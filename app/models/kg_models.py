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
        'page': 0, 
        'total': 1, 
        'num_of_pages': 1, 
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
                    'feedback': 'Resource http://10.3.7.220/kg/v1/resources/charite/VRE_Datasets/_/1634922993 already exists in project charite/VRE_Datasets'
                    }
                    }
                }
            }
    )
