from ..commons.data_providers.data_models import DataManifestModel
from ..commons.data_providers.data_models import DataAttributeModel
from ..commons.data_providers.data_models import DatasetVersionModel
from logger import LoggerFactory
from sqlalchemy.future import select


class RDConnection:
    def __init__(self):
        self._logger = LoggerFactory("Helpers").get_logger()

    async def get_manifest_name_from_project_db(self, event: dict, db) -> list:
        self._logger.info(
            "get_manifest_name_from_project_db".center(80, '-')
            )
        self._logger.info(f"Received event: {event}")
        project_code = event.get('project_code')
        manifest_name = event.get('manifest_name', None)
        try:
            if manifest_name:
                m = await db.execute(
                    select(DataManifestModel).filter_by(
                        project_code=project_code,
                        name=manifest_name))
                self._logger.info(f"QUERY db RESULT: {type(m)}")
                m_result = m.scalars().first()
                if not m_result:
                    self._logger.debug(f"{m_result}")
                    self._logger.debug("not m_result")
                    return []
                else:
                    manifest = [{'name': m_result.name, 'id': m_result.id}]
                    return manifest
            else:
                manifests = await db.execute(
                    select(DataManifestModel).filter_by(
                        project_code=project_code))
                self._logger.info(f"QUERY db RESULT: {manifests}")
                manifests_result = manifests.scalars().all()
                self._logger.info(f"QUERY RESULT: {manifests_result}")
                manifest_in_project = []
                for m in manifests_result:
                    manifest = {'name': m.name, 'id': m.id}
                    manifest_in_project.append(manifest)
                return manifest_in_project
        except Exception as e:
            self._logger.error(
                f"ERROR get_manifest_name_from_project_db: {e}"
                )
            raise e

    async def get_attributes_in_manifest_db(self, manifests: list, db) -> dict:
        self._logger.info("get_attributes_in_manifest_db".center(80, '-'))
        self._logger.info(f"Received event: {manifests}")
        manifest_list = []
        for manifest in manifests:
            manifest_id = manifest.get('id')
            manifest_list.append(manifest_id)
        id_list = set(manifest_list)
        results = await db.execute(
            select(DataAttributeModel).filter(
                DataAttributeModel.manifest_id.in_(id_list)))
        self._logger.debug(f"Result of attributes are {results}")
        attributes = results.scalars().all()
        self._logger.info(f"attributes is {attributes}")
        if not attributes:
            return {}
        manifest_attributes = manifests
        for m in manifest_attributes:
            self._logger.info(f"Each attributes is {m}")
            m['manifest_name'] = m.get('name')
            m.pop('name')
            m['attributes'] = [
                {
                    "name": attr.name,
                    "type": attr.type,
                    "optional": attr.optional,
                    "value": attr.value
                    } for attr in attributes if attr.manifest_id == m.get('id')
                    ]
            self._logger.info(f"Each attributes payload is {m['attributes']}")
        return manifest_attributes

    async def get_dataset_versions(self, event, db):
        self._logger.info("get_dataset_versions".center(80, '-'))
        self._logger.info(f'Query event: {event}')
        dataset_geid = event.get('dataset_geid')
        dataset_versions = []
        results = await db.execute(
            select(DatasetVersionModel).filter_by(
                dataset_geid=dataset_geid))
        versions = results.scalars().all()
        self._logger.info(f"Query result: {versions}")
        if not versions:
            return []
        for attr in versions:
            result = {"dataset_code": attr.dataset_code,
                      "dataset_geid": attr.dataset_geid,
                      "version": attr.version,
                      "created_by": attr.created_by,
                      "created_at": str(attr.created_at),
                      "location": attr.location,
                      "notes": attr.notes
                      }
            dataset_versions.append(result)
        return dataset_versions
