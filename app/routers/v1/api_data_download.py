import os
import time
from fastapi import APIRouter, BackgroundTasks
from fastapi_utils import cbv
from fastapi.responses import FileResponse
from ...models.models_data_download import EDataDownloadStatus, PreDataDowanloadPOST, PreDataDowanloadResponse, GetDataDownloadStatusRespon
from ...models.base_models import APIResponse, EAPIResponseCode
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.download_token_manager import verify_download_token, generate_token
from ...resources.error_handler import catch_internal, ECustomizedError, customized_error_template
from ...resources.helpers import generate_zipped_file_path, zip_multi_files, set_status, get_status
from ...config import ConfigClass

router = APIRouter()

_API_TAG = 'v1/data-download'
_API_NAMESPACE = "api_data_download"


@cbv.cbv(router)
class APIDataDownload:
    '''
    API Data Download Class
    '''

    def __init__(self):
        self.__logger = SrvLoggerFactory('api_data_download').get_logger()

    @router.post("/pre-download", tags=[_API_TAG], response_model=PreDataDowanloadResponse,
                 summary="Pre download process, zip as a package if more than 1 file")
    @catch_internal(_API_NAMESPACE)
    async def data_pre_download(self, request_payload: PreDataDowanloadPOST, background_tasks: BackgroundTasks):
        '''
        "files":
        [{
            "full_path": "",
            "project_code": "",
            "geid": ""
        }]
        '''
        response = APIResponse()
        files = request_payload.files
        job_id = "data-download-" + str(int(time.time()))
        job_status = EDataDownloadStatus.INIT
        # check if number of files valid
        if len(files) < 1:
            response.code = EAPIResponseCode.bad_request
            response.result = None
            response.error_msg = customized_error_template(
                ECustomizedError.INVALID_FILE_AMOUNT)
            return response.json_response()
        full_path = files[0]["full_path"]
        # if multiple files, zip as one file
        if len(files) > 1:
            # asyncly zip files
            zipped_file_path = generate_zipped_file_path(request_payload.project_code)
            full_path = zipped_file_path
            # update status as zipping
            job_status = EDataDownloadStatus.ZIPPING
        else:
            # update status as ready for download
            job_status = EDataDownloadStatus.READY_FOR_DOWNLOADING
        # generate jwt hash code token
        hash_code = generate_token({
            "full_path":  full_path, # geid
            "issuer": "SERVICE DATA DOWNLOAD",
            "operator": request_payload.operator,
            "session_id": request_payload.session_id,
            "job_id": job_id,
            "project_code": request_payload.project_code,
            "iat": int(time.time()),
            "exp": int(time.time()) + (ConfigClass.DOWNLOAD_TOKEN_EXPIRE_AT * 60)
        })
        if len(files) > 1:
            background_tasks.add_task(
                zip_worker, job_id, zipped_file_path, files, request_payload, hash_code)
        # set status in session store
        job_recorded = set_status(
            request_payload.session_id,
            job_id,
            full_path,
            "data_download",
            job_status.name,
            request_payload.project_code,
            request_payload.operator,
            payload={
                "hash_code": hash_code
            }
        )
        response.result = job_recorded
        response.code = EAPIResponseCode.success
        return response.json_response()

    @router.get("/download/status/{hash_code}", tags=[_API_TAG], response_model=GetDataDownloadStatusRespon,
                summary="Check download status")
    @catch_internal(_API_NAMESPACE)
    async def data_download_status(self, hash_code):
        '''
        Check download status
        '''
        response = APIResponse()
        # verify hash code
        res_verify_token = verify_download_token(hash_code)
        if not res_verify_token[0]:
            response.code = EAPIResponseCode.unauthorized
            response.result = None
            response.error_msg = res_verify_token[1]
            return response.json_response()
        else:
            res_verify_token = res_verify_token[1]
        session_id = res_verify_token['session_id']
        job_id = res_verify_token['job_id']
        project_code = res_verify_token['project_code']
        operator = res_verify_token['operator']
        job_fatched = get_status(
            session_id, job_id, project_code, "data_download", operator)
        found = False
        if len(job_fatched) > 0:
            # find target source
            job_fatched = [job for job in job_fatched if job['source']
                           == res_verify_token['full_path']]
            if len(job_fatched) > 0:
                found = True
                job_fatched = job_fatched[0]
        if found:
            response.code = EAPIResponseCode.success
            response.result = job_fatched
            return response.json_response()
        else:
            response.code = EAPIResponseCode.not_found
            response.result = job_fatched
            response.error_msg = customized_error_template(
                ECustomizedError.JOB_NOT_FOUND)
            return response.json_response()

    @router.get("/download/{hash_code}", tags=[_API_TAG],
                summary="Download the data, asynchronously streams a file as the response.")
    @catch_internal(_API_NAMESPACE)
    async def data_download(self, hash_code: str):
        '''
        If succeed, asynchronously streams a FileResponse
        '''
        response = APIResponse()
        self.__logger.info(
            'Check downloading request: %s' % hash_code)

        # Verify and decode token
        res_verify_token = verify_download_token(hash_code)
        if not res_verify_token[0]:
            response.code = EAPIResponseCode.unauthorized
            response.result = None
            response.error_msg = res_verify_token[1]
            return response.json_response()
        else:
            res_verify_token = res_verify_token[1]

        # Use root to generate the path
        if not os.path.exists(res_verify_token['full_path']):
            response.code = EAPIResponseCode.not_found
            response.result = None
            response.error_msg = customized_error_template(
                ECustomizedError.FILE_NOT_FOUND) % res_verify_token['full_path']
            return response.json_response()

        filename = os.path.basename(res_verify_token['full_path'])

        return FileResponse(path=res_verify_token['full_path'], filename=filename)


def zip_worker(job_id, zipped_file_path, files, request_payload: PreDataDowanloadPOST, hash_code):
    '''
    async zip worker
    '''
    try:
        res = zip_multi_files(zipped_file_path, files)
        set_status(
            request_payload.session_id,
            job_id,
            zipped_file_path,
            "data_download",
            EDataDownloadStatus.READY_FOR_DOWNLOADING.name,
            request_payload.project_code,
            request_payload.operator,
            payload={
                "hash_code": hash_code
            }
        )
    except Exception as e:
        set_status(
            request_payload.session_id,
            job_id,
            zipped_file_path,
            "data_download",
            EDataDownloadStatus.CANCELLED.name,
            request_payload.project_code,
            request_payload.operator,
            payload={
                "hash_code": hash_code,
                "error_msg": str(e)
            }
        )
