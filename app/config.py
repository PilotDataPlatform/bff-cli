import os
# os.environ['env'] = 'test'


class ConfigClass(object):
    env = os.environ.get('env', 'test')

    version = "0.1.0"
    if env == 'test':
        NEO4J_SERVICE = "http://10.3.7.216:5062/v1/neo4j/"
        NEO4J_SERVICE_v2 = "http://10.3.7.216:5062/v2/neo4j/"
        FILEINFO_HOST = "http://10.3.7.228:5066"
        AUTH_SERVICE = "http://10.3.7.217:5061"
        RDS_HOST = '10.3.7.215'
        UPLOAD_VRE = "http://10.3.7.200:5079"
        UPLOAD_GREENROOM = "http://10.3.7.201:5079"
        COMMON_SERVICE = "http://10.3.7.222:5062/v1/utility/id"
        url_download_greenroom = "http://10.3.7.220/vre/api/vre/portal/download/gr/v1/download/pre/"
        url_download_vrecore = "http://10.3.7.220/vre/api/vre/portal/download/vre/v1/download/pre/"
    else:
        NEO4J_SERVICE = "http://neo4j.utility:5062/v1/neo4j/"
        NEO4J_SERVICE_v2 = "http://neo4j.utility:5062/v2/neo4j/"
        FILEINFO_HOST = "http://entityinfo.utility:5066"
        AUTH_SERVICE = "http://auth.utility:5061"
        RDS_HOST = "opsdb.utility"
        UPLOAD_VRE = "http://upload.vre:5079"
        UPLOAD_GREENROOM = "http://upload.greenroom:5079"
        COMMON_SERVICE = "http://common.utility:5062/v1/utility/id"
        url_download_greenroom = "http://download.greenroom:5077/v1/download/pre/"
        url_download_vrecore = "http://download.vre:5077/v1/download/pre/"

    PROVENANCE_SERVICE = "http://provenance.utility:5077"

    RDS_PORT = "5432"
    RDS_DBNAME = "INDOC_VRE"
    RDS_USER = "postgres"
    RDS_PWD = "postgres"
    if env == 'charite':
        RDS_USER = "indoc_vre"
        RDS_PWD = "opsdb-jrjmfa9svvC"
    RDS_SCHEMA_DEFAULT = "indoc_vre"

    SQLALCHEMY_DATABASE_URI = f"postgres://{RDS_USER}:{RDS_PWD}@{RDS_HOST}/{RDS_DBNAME}"
