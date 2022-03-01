from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.dataset_models import *
from ...models.base_models import EAPIResponseCode
from ...resources.error_handler import catch_internal, customized_error_template, ECustomizedError
from ...resources.database_service import RDConnection
from ...resources.dependencies import jwt_required, get_node
from app.resources.helpers import get_user_datasets
from logger import LoggerFactory


router = APIRouter()
_API_TAG = 'V1 dataset'
_API_NAMESPACE = "api_dataset"


@cbv(router)
class APIDataset:
    current_identity: dict = Depends(jwt_required)

    def __init__(self):
        self._logger = LoggerFactory(_API_NAMESPACE).get_logger()
        self.db = RDConnection()

    @router.get("/datasets", tags=[_API_TAG],
                response_model=DatasetListResponse,
                summary="Get dataset list that user have access to")
    @catch_internal(_API_NAMESPACE)
    async def list_datasets(self):
        '''
        Get the dataset list that user have access to
        '''
        self._logger.info("API list_datasets".center(80, '-'))
        api_response = DatasetListResponse()
        try:
            username = self.current_identity['username']
        except (AttributeError, TypeError):
            return self.current_identity
        self._logger.info(f"User request with identity: {self.current_identity}")
        dataset_list = get_user_datasets(username)
        self._logger.info(f"Getting user datasets: {dataset_list}")
        self._logger.info(f"Number of datasets: {len(dataset_list)}")
        api_response.result = dataset_list
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()

    @router.get("/dataset/{dataset_code}", tags=[_API_TAG],
                response_model=DatasetDetailResponse,
                summary="Get dataset detail based on the dataset code")
    @catch_internal(_API_NAMESPACE)
    async def get_dataset(self, dataset_code):
        '''
        Get the dataset detail by dataset code
        '''
        self._logger.info("API validate_manifest".center(80, '-'))
        api_response = DatasetDetailResponse()
        try:
            username = self.current_identity['username']
        except (AttributeError, TypeError):
            return self.current_identity
        self._logger.info("API list_datasets".center(80, '-'))
        self._logger.info(f"User request with identity: {self.current_identity}")
        node = get_node({"code": dataset_code}, 'Dataset')
        self._logger.info(f"Getting user dataset node: {node}")
        if not node:
            api_response.code = EAPIResponseCode.not_found
            api_response.error_msg = customized_error_template(ECustomizedError.DATASET_NOT_FOUND)
            return api_response.json_response()
        elif node.get('creator') != username:
            api_response.code = EAPIResponseCode.forbidden
            api_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
            return api_response.json_response()
        elif 'Dataset' not in node.get('labels'):
            api_response.code = EAPIResponseCode.not_found
            api_response.error_msg = customized_error_template(ECustomizedError.DATASET_NOT_FOUND)
            return api_response.json_response()
        node_geid = node.get('global_entity_id')
        dataset_query_event = {
            'dataset_geid': node_geid,
            }
        versions = self.db.get_dataset_versions(dataset_query_event)
        dataset_detail = {'general_info': node, 'version_detail': versions, 'version_no': len(versions)}
        api_response.result = dataset_detail
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()


