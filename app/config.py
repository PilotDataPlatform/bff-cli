import os

class ConfigClass(object):
    env = os.environ.get('env')

    version = "0.1.0"
    VRE_ROOT_PATH = "/vre-data"
    # NEO4J_SERVICE = "http://neo4j.utility:5062/v1/neo4j/"
    NEO4J_SERVICE = "http://10.3.7.216:5062/v1/neo4j/"
    NEO4J_HOST = "http://neo4j.utility:5062"
    FILEINFO_HOST = "http://entityinfo.utility:5066"
    METADATA_API = "http://cataloguing.utility:5064"
    SEND_MESSAGE_URL = "http://queue-producer.greenroom:6060/v1/send_message"
    DATA_OPS_GR = "http://dataops-gr.greenroom:5063"
    # utility service
    UTILITY_SERVICE = "http://common.utility:5062"

    # disk mounts
    NFS_ROOT_PATH = "./"
    VRE_ROOT_PATH = "/vre-data"

    # download secret
    DOWNLOAD_KEY = "indoc101"
    DOWNLOAD_TOKEN_EXPIRE_AT = 5

    # Redis Service
    # REDIS_HOST = "10.3.7.233"
    REDIS_HOST = "redis-master.utility"
    REDIS_PORT = 6379
    REDIS_DB = 0
    REDIS_PASSWORD = {
        'staging': '8EH6QmEYJN',
        'charite': 'o2x7vGQx6m'
    }.get(env, "5wCCMMC1Lk")