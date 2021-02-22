import os


class ConfigClass(object):
    env = os.environ.get('env')

    version = "0.1.0"
    VRE_ROOT_PATH = "/vre-data"
    # NEO4J_SERVICE = "http://neo4j.utility:5062/v1/neo4j/"
    NEO4J_SERVICE = "http://10.3.7.216:5062/v1/neo4j/"
    NEO4J_HOST = "http://neo4j.utility:5062"
    # FILEINFO_HOST = "http://entityinfo.utility:5066"
    FILEINFO_HOST = "http://10.3.7.228:5066/"
    METADATA_API = "http://cataloguing.utility:5064"
    SEND_MESSAGE_URL = "http://queue-producer.greenroom:6060/v1/send_message"
    DATA_OPS_GR = "http://dataops-gr.greenroom:5063"
    # utility service
    UTILITY_SERVICE = "http://common.utility:5062"

    # RDS_HOST = "opsdb.utility"
    RDS_HOST = '10.3.7.215'
    RDS_PORT = "5432"
    RDS_DBNAME = "INDOC_VRE"
    RDS_USER = "postgres"
    RDS_PWD = "postgres"
    if env == 'charite':
        RDS_USER = "indoc_vre"
        RDS_PWD = "opsdb-jrjmfa9svvC"
    RDS_SCHEMA_DEFAULT = "indoc_vre"

    SQLALCHEMY_DATABASE_URI = f"postgres://{RDS_USER}:{RDS_PWD}@{RDS_HOST}/{RDS_DBNAME}"
