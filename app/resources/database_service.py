from ..commons.data_providers.data_models import DataManifestModel, DataAttributeModel, DatasetVersionModel
from ..commons.data_providers.database import DBConnection
from ..service_logger.logger_factory_service import SrvLoggerFactory


class RDConnection:
    
    def __init__(self):
        self._logger = SrvLoggerFactory("Helpers").get_logger()
        db = DBConnection()
        self.db_session = db.session

    def get_manifest_name_from_project_in_db(self, event: dict)-> list:
        self._logger.info("get_manifest_name_from_project_in_db".center(80, '-'))
        self._logger.info(f"Received event: {event}")
        project_code = event.get('project_code')
        manifest_name = event.get('manifest_name', None)
        try:
            if manifest_name:
                m = self.db_session.query(DataManifestModel.name,
                                    DataManifestModel.id)\
                    .filter_by(project_code=project_code, name=manifest_name)\
                    .first()
                self._logger.info(f"QUERY RESULT: {m}")
                if not m:
                    return []
                else:
                    manifest = [{'name': m[0], 'id': m[1]}]
                    return manifest
            else:
                manifests = self.db_session.query(DataManifestModel.name,
                                            DataManifestModel.id)\
                    .filter_by(project_code=project_code)\
                    .all()
                self._logger.info(f"QUERY RESULT: {manifests}")
                manifest_in_project = []
                for m in manifests:
                    manifest = {'name': m[0], 'id': m[1]}
                    manifest_in_project.append(manifest)
                return manifest_in_project
        except Exception as e:
            self._logger.error(f"ERROR get_manifest_name_from_project_in_db: {e}")
            raise e
    
    def get_attributes_in_manifest_in_db(self, manifests: list) -> dict:
        self._logger.info("get_attributes_in_manifest_in_db".center(80, '-'))
        self._logger.info(f"Received event: {manifests}")
        manifest_list = []
        for manifest in manifests:
                manifest_id = manifest.get('id')
                manifest_list.append(manifest_id)
        id_list = set(manifest_list)
        attributes = self.db_session.query(DataAttributeModel.name,
                                    DataAttributeModel.type,
                                    DataAttributeModel.optional,
                                    DataAttributeModel.value,
                                    DataAttributeModel.manifest_id). \
            filter(DataAttributeModel.manifest_id.in_(id_list)). \
            order_by(DataAttributeModel.id.asc()).all()
        self._logger.info(attributes)
        if not attributes:
            return {}
        manifest_attributes = manifests
        for m in manifest_attributes:
            m['manifest_name'] = m.get('name')
            m.pop('name')
            m['attributes'] = [{"name": attr[0], "type": attr[1], "optional": attr[2],
                                "value": attr[3]} for attr in attributes if attr[4] == m.get('id')]
        return manifest_attributes


    def get_dataset_versions(self, event):
        self._logger.info("get_dataset_versions".center(80, '-'))
        self._logger.info(f'Query event: {event}')
        dataset_geid = event.get('dataset_geid')
        dataset_versions = []
        versions = self.db_session.query(DatasetVersionModel.dataset_code,
                                    DatasetVersionModel.dataset_geid,
                                    DatasetVersionModel.version,
                                    DatasetVersionModel.created_by,
                                    DatasetVersionModel.created_at,
                                    DatasetVersionModel.location,
                                    DatasetVersionModel.notes). \
            filter_by(dataset_geid=dataset_geid). \
            order_by(DatasetVersionModel.id.asc()).all()
        self._logger.info(f"Query result: {versions}")
        if not versions:
            return []
        for attr in versions:
            result = {"dataset_code": attr[0],
                    "dataset_geid": attr[1],
                    "version": attr[2],
                    "created_by": attr[3],
                    "created_at": str(attr[4]),
                    "location": attr[5],
                    "notes": attr[6]
                    }
            dataset_versions.append(result)
        return dataset_versions