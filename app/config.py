import os


class ConfigClass(object):
    env = os.environ.get('env')

    version = "0.1.0"
    NEO4J_SERVICE = "http://neo4j.utility:5062/v1/neo4j/"
    # NEO4J_SERVICE = "http://10.3.7.216:5062/v1/neo4j/"
    FILEINFO_HOST = "http://entityinfo.utility:5066"
    # FILEINFO_HOST = "http://10.3.7.228:5066"
    UPLOAD_VRE = "http://upload.vre:5079"
    UPLOAD_GREENROOM = "http://upload.greenroom:5079"
    AUTH_SERVICE = "http://auth.utility:5061"
    PROVENANCE_SERVICE = "http://provenance.utility:5077"

    RDS_HOST = "opsdb.utility"
    # RDS_HOST = '10.3.7.215'
    RDS_PORT = "5432"
    RDS_DBNAME = "INDOC_VRE"
    RDS_USER = "postgres"
    RDS_PWD = "postgres"
    if env == 'charite':
        RDS_USER = "indoc_vre"
        RDS_PWD = "opsdb-jrjmfa9svvC"
    RDS_SCHEMA_DEFAULT = "indoc_vre"

    SQLALCHEMY_DATABASE_URI = f"postgres://{RDS_USER}:{RDS_PWD}@{RDS_HOST}/{RDS_DBNAME}"
