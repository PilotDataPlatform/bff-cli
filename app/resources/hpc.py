from ..models.error_model import HPCError
from logger import LoggerFactory
from ..config import ConfigClass
from ..models.base_models import EAPIResponseCode
import httpx

_logger = LoggerFactory("HPC").get_logger()

async def get_hpc_jwt_token(token_issuer, username, password = None):
    _logger.info("get_hpc_jwt_token".center(80, '-'))
    try:
        payload = {
            "token_issuer": token_issuer,
            "username": username,
            "password": password
            }
        url = ConfigClass.HPC_SERVICE + "/v1/hpc/auth"
        _logger.info(f"Request url: {url}")
        _logger.info(f"Request payload: {payload}")
        async with httpx.AsyncClient() as client:
            res = await client.post(url, json=payload)
        _logger.info(f"Response: {res.text}")
        _logger.info(f"Response: {res.json()}")
        token = res.json().get('result')
    except Exception as e:
        _logger.error(e)
        token = ''
    finally:
        return token

async def submit_hpc_job(job_submission_event) -> dict:
    _logger.info("submit_hpc_job".center(80, '-'))
    try:
        _logger.info(f"Received event: {job_submission_event}")
        token = job_submission_event.token
        host = job_submission_event.host
        username = job_submission_event.username
        job_info = job_submission_event.job_info
        job_script = job_info.get('script', '')
        hpc_host = host.split('://')
        if len(hpc_host) < 2:
            raise HPCError(EAPIResponseCode.bad_request, "HPC protocal required")
        slurm_host = hpc_host[1]
        protocol_type = hpc_host[0]
        _logger.info(f"Request job script: {job_script}")
        if not job_script:
            status_code = EAPIResponseCode.bad_request
            error_msg = 'Missing script'
            raise HPCError(status_code, error_msg)
        url = ConfigClass.HPC_SERVICE + "/v1/hpc/job"
        headers = {
            "Authorization": token
        }
        payload = {
            "slurm_host": slurm_host,
            "username": username,
            "job_info": job_info,
            'protocol': protocol_type
        }
        _logger.info(f"Request url: {url}")
        _logger.info(f"Request headers: {headers}")
        _logger.info(f"Request payload: {payload}")
        async with httpx.AsyncClient() as client:
            res = await client.post(url, headers=headers, json=payload)
        _logger.info(f"Response: {res.json()}")
        response = res.json()
        status_code = response.get('code')
        if status_code == 200:
            result = response.get('result')
            return result
        elif status_code == 400:
            error_msg = response.get('error_msg')
            if "Jobs description entry not found, empty or not dictionary or list" in error_msg:
                raise HPCError(EAPIResponseCode.bad_request, "Jobs description entry not found, empty or not dictionary or list")
        elif status_code == 500:
            error_msg = response.get('error_msg')
            if "Zero Bytes were transmitted or received" in error_msg:
                raise HPCError(EAPIResponseCode.forbidden, "HPC token expired")
        else:
            error_msg = response.get('error_msg')
            raise HPCError(EAPIResponseCode.internal_error, error_msg)
    except Exception as e:
        _logger.error(e)
        raise e

async def get_hpc_job_info(job_id, host, username, token) -> dict:
    _logger.info("get_hpc_job_info".center(80, '-'))
    try:
        hpc_host = host.split('://')
        if len(hpc_host) < 2:
            raise HPCError(EAPIResponseCode.bad_request, "HPC protocal required")
        slurm_host = hpc_host[1]
        protocol_type = hpc_host[0]
        _logger.info(f"Received job_id: {job_id}")
        url = ConfigClass.HPC_SERVICE + f"/v1/hpc/job/{job_id}"
        headers = {
            "Authorization": token
        }
        params = {
            "slurm_host": slurm_host,
            "username": username,
            "protocol": protocol_type
        }
        _logger.info(f"Request url: {url}")
        _logger.info(f"Request headers: {headers}")
        _logger.info(f"Request params: {params}")
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, params=params)
        _logger.info(f"Response: {res.text}")
        response = res.json()
        status_code = response.get('code')
        if status_code == 200:
            result = response.get('result')
            return result
        else:
            error_msg = response.get('error_msg')
            if 'unknown job' in error_msg:
                error_msg = 'Job ID not found'
                status_code = EAPIResponseCode.not_found
                raise HPCError(status_code, error_msg)
            elif 'Unable find requested URL' in error_msg:
                error_msg = 'Host not found'
                status_code = EAPIResponseCode.not_found
                raise HPCError(status_code, error_msg)
            else:
                raise Exception(status_code, error_msg)
    except Exception as e:
        _logger.error(e)
        raise e

async def get_hpc_nodes(host, username, hpc_token) -> dict:
    _logger.info("get_hpc_nodes".center(80, '-'))
    try:
        _logger.info(f"Received host: {host}")
        _logger.info(f"Received username: {username}")
        hpc_host = host.split('://')
        if len(hpc_host) < 2:
            raise HPCError(EAPIResponseCode.bad_request, "HPC protocal required")
        slurm_host = hpc_host[1]
        protocol_type = hpc_host[0]
        url = ConfigClass.HPC_SERVICE + f"/v1/hpc/nodes"
        headers = {
            "Authorization": hpc_token
        }
        params = {
            "slurm_host": slurm_host,
            "username": username,
            "protocol": protocol_type
        }
        _logger.info(f"Request url: {url}")
        _logger.info(f"Request headers: {headers}")
        _logger.info(f"Request params: {params}")
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, params=params)
        _logger.info(f"Response: {res.text}")
        response = res.json()
        status_code = response.get('code')
        if status_code == 200:
            result = response.get('result')
            return result
        else:
            error_msg = response.get('error_msg')
            status_code = EAPIResponseCode.internal_error
            raise HPCError(status_code, error_msg)
    except Exception as e:
        _logger.error(e)
        raise e

async def get_hpc_node_by_name(host, username, hpc_token, node_name) -> dict:
    _logger.info("get_hpc_node_by_name".center(80, '-'))
    try:
        _logger.info(f"Received host: {host}")
        _logger.info(f"Received username: {username}")
        _logger.info(f"Received nodename: {node_name}")
        hpc_host = host.split('://')
        if len(hpc_host) < 2:
            raise HPCError(EAPIResponseCode.bad_request, "HPC protocal required")
        slurm_host = hpc_host[1]
        protocol_type = hpc_host[0]
        url = ConfigClass.HPC_SERVICE + f"/v1/hpc/nodes/{node_name}"
        headers = {
            "Authorization": hpc_token
        }
        params = {
            "slurm_host": slurm_host,
            "username": username,
            "protocol": protocol_type
        }
        _logger.info(f"Request url: {url}")
        _logger.info(f"Request headers: {headers}")
        _logger.info(f"Request params: {params}")
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, params=params)
        _logger.info(f"Response: {res.text}")
        response = res.json()
        status_code = response.get('code')
        if status_code == 200:
            result = response.get('result')
            return result
        else:
            error_msg = response.get('error_msg')
            if 'Invalid node name specified' in error_msg:
                error_msg = 'Node name not found'
                status_code = EAPIResponseCode.not_found
                raise HPCError(status_code, error_msg)
            else:
                status_code = EAPIResponseCode.internal_error
                raise HPCError(status_code, error_msg)
    except Exception as e:
        _logger.error(e)
        raise e

async def get_hpc_partitions(host, username, hpc_token) -> dict:
    _logger.info("get_hpc_partitions".center(80, '-'))
    try:
        _logger.info(f"Received host: {host}")
        _logger.info(f"Received username: {username}")
        hpc_host = host.split('://')
        if len(hpc_host) < 2:
            raise HPCError(EAPIResponseCode.bad_request, "HPC protocal required")
        slurm_host = hpc_host[1]
        protocol_type = hpc_host[0]
        url = ConfigClass.HPC_SERVICE + f"/v1/hpc/partitions"
        headers = {
            "Authorization": hpc_token
        }
        params = {
            "slurm_host": slurm_host,
            "username": username,
            "protocol": protocol_type
        }
        _logger.info(f"Request url: {url}")
        _logger.info(f"Request headers: {headers}")
        _logger.info(f"Request params: {params}")
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, params=params)
        _logger.info(f"Response: {res.text}")
        response = res.json()
        status_code = response.get('code')
        if status_code == 200:
            result = response.get('result')
            return result
        else:
            error_msg = response.get('error_msg')
            if 'Retrieval of HPC partitions info failed' in error_msg:
                error_msg = 'Cannot list partitions, please check if hpc token valid'
                status_code = EAPIResponseCode.bad_request
                raise HPCError(status_code, error_msg)
            else:
                status_code = EAPIResponseCode.internal_error
                raise HPCError(status_code, error_msg)
    except Exception as e:
        _logger.error(e)
        raise e

async def get_hpc_partition_by_name(host, username, hpc_token, partition_name) -> dict:
    _logger.info("get_hpc_partition_by_name".center(80, '-'))
    try:
        _logger.info(f"Received host: {host}")
        _logger.info(f"Received username: {username}")
        _logger.info(f"Received partition_name: {partition_name}")
        hpc_host = host.split('://')
        if len(hpc_host) < 2:
            raise HPCError(EAPIResponseCode.bad_request, "HPC protocal required")
        slurm_host = hpc_host[1]
        protocol_type = hpc_host[0]
        url = ConfigClass.HPC_SERVICE + f"/v1/hpc/partitions/{partition_name}"
        headers = {
            "Authorization": hpc_token
        }
        params = {
            "slurm_host": slurm_host,
            "username": username,
            "protocol": protocol_type
        }
        _logger.info(f"Request url: {url}")
        _logger.info(f"Request headers: {headers}")
        _logger.info(f"Request params: {params}")
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, params=params)
        _logger.info(f"Response: {res.text}")
        response = res.json()
        status_code = response.get('code')
        if status_code == 200:
            result = response.get('result')
            return result
        else:
            error_msg = response.get('error_msg')
            if 'Invalid partition name specified' in error_msg:
                error_msg = 'Partition name not found'
                status_code = EAPIResponseCode.not_found
                raise HPCError(status_code, error_msg)
            else:
                status_code = EAPIResponseCode.internal_error
                raise HPCError(status_code, error_msg)
    except Exception as e:
        _logger.error(e)
        raise e
