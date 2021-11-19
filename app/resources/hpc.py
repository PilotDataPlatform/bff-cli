from ..models.error_model import HPCError
from ..service_logger.logger_factory_service import SrvLoggerFactory
import requests
from ..config import ConfigClass
from ..models.base_models import APIResponse, EAPIResponseCode

_logger = SrvLoggerFactory("HPC").get_logger()

def submit_hpc_job(job_submission_event) -> dict:
    _logger.info("submit_hpc_job".center(80, '-'))
    try:
        _logger.info(f"Received event: {job_submission_event}")
        token = job_submission_event.token
        host = job_submission_event.host
        username = job_submission_event.username
        job_info = job_submission_event.job_info
        job_script = job_info.get('script', '')
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
            "slurm_host": host,
            "username": username,
            "job_info": job_info
        }
        _logger.info(f"Request url: {url}")
        _logger.info(f"Request headers: {headers}")
        _logger.info(f"Request payload: {payload}")
        res = requests.post(url, headers=headers, json=payload)
        _logger.info(f"Response: {res.text}")
        response = res.json()
        status_code = response.get('code')
        if status_code == 200:
            result = response.get('result')
            return result
        else:
            error_msg = response.get('error_msg')
            raise HPCError(status_code, error_msg)
    except Exception as e:
        _logger.error(e)
        raise e

def get_hpc_job_info(job_id, host, username, token) -> dict:
    _logger.info("get_hpc_job_info".center(80, '-'))
    try:
        _logger.info(f"Received job_id: {job_id}")
        url = ConfigClass.HPC_SERVICE + f"/v1/hpc/job/{job_id}"
        headers = {
            "Authorization": token
        }
        params = {
            "slurm_host": host,
            "username": username
        }
        _logger.info(f"Request url: {url}")
        _logger.info(f"Request headers: {headers}")
        _logger.info(f"Request params: {params}")
        res = requests.get(url, headers=headers, params=params)
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
            else:
                raise Exception(status_code, error_msg)
    except Exception as e:
        _logger.error(e)
        raise e

def get_hpc_nodes(host, username, hpc_token) -> dict:
    _logger.info("get_hpc_nodes".center(80, '-'))
    try:
        _logger.info(f"Received host: {host}")
        _logger.info(f"Received username: {username}")
        url = ConfigClass.HPC_SERVICE + f"/v1/hpc/nodes"
        headers = {
            "Authorization": hpc_token
        }
        params = {
            "slurm_host": host,
            "username": username
        }
        _logger.info(f"Request url: {url}")
        _logger.info(f"Request headers: {headers}")
        _logger.info(f"Request params: {params}")
        res = requests.get(url, headers=headers, params=params)
        _logger.info(f"Response: {res.text}")
        response = res.json()
        status_code = response.get('code')
        if status_code == 200:
            result = response.get('result')
            return result
        else:
            error_msg = response.get('error_msg')
            raise HPCError(status_code, error_msg)
    except Exception as e:
        _logger.error(e)
        raise e

def get_hpc_node_by_name(host, username, hpc_token, node_name) -> dict:
    _logger.info("get_hpc_node_by_name".center(80, '-'))
    try:
        _logger.info(f"Received host: {host}")
        _logger.info(f"Received username: {username}")
        _logger.info(f"Received nodename: {node_name}")
        url = ConfigClass.HPC_SERVICE + f"/v1/hpc/nodes/{node_name}"
        headers = {
            "Authorization": hpc_token
        }
        params = {
            "slurm_host": host,
            "username": username
        }
        _logger.info(f"Request url: {url}")
        _logger.info(f"Request headers: {headers}")
        _logger.info(f"Request params: {params}")
        res = requests.get(url, headers=headers, params=params)
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
            raise HPCError(status_code, error_msg)
    except Exception as e:
        _logger.error(e)
        raise e

def get_hpc_partitions(host, username, hpc_token) -> dict:
    _logger.info("get_hpc_partitions".center(80, '-'))
    try:
        _logger.info(f"Received host: {host}")
        _logger.info(f"Received username: {username}")
        url = ConfigClass.HPC_SERVICE + f"/v1/hpc/partitions"
        headers = {
            "Authorization": hpc_token
        }
        params = {
            "slurm_host": host,
            "username": username
        }
        _logger.info(f"Request url: {url}")
        _logger.info(f"Request headers: {headers}")
        _logger.info(f"Request params: {params}")
        res = requests.get(url, headers=headers, params=params)
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
            raise HPCError(status_code, error_msg)
    except Exception as e:
        _logger.error(e)
        raise e

def get_hpc_partition_by_name(host, username, hpc_token, partition_name) -> dict:
    _logger.info("get_hpc_partition_by_name".center(80, '-'))
    try:
        _logger.info(f"Received host: {host}")
        _logger.info(f"Received username: {username}")
        _logger.info(f"Received partition_name: {partition_name}")
        url = ConfigClass.HPC_SERVICE + f"/v1/hpc/partitions/{partition_name}"
        headers = {
            "Authorization": hpc_token
        }
        params = {
            "slurm_host": host,
            "username": username
        }
        _logger.info(f"Request url: {url}")
        _logger.info(f"Request headers: {headers}")
        _logger.info(f"Request params: {params}")
        res = requests.get(url, headers=headers, params=params)
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
            raise HPCError(status_code, error_msg)
    except Exception as e:
        _logger.error(e)
        raise e
