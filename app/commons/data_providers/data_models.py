from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime
from ...config import ConfigClass
from .database import Base
from sqlalchemy.types import Enum


class TypeEnum(Enum):
    text = 'text'
    multiple_choice = 'multiple_choice'


class DataManifestModel(Base):
    __tablename__ = 'data_manifest'
    __table_args__ = {"schema": ConfigClass.RDS_SCHEMA_DEFAULT}

    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String())
    project_code = Column(String())

    def __init__(self, name, project_code):
        self.name = name
        self.project_code = project_code

    def to_dict(self):
        result = {}
        for field in ["id", "name", "project_code"]:
            result[field] = getattr(self, field)
        return result


class DataAttributeModel(Base):
    __tablename__ = 'data_attribute'
    __table_args__ = {"schema": ConfigClass.RDS_SCHEMA_DEFAULT}
    id = Column(Integer, unique=True, primary_key=True)
    manifest_id = Column(Integer, ForeignKey(DataManifestModel.id))
    name = Column(String())
    type = Column(Enum('text', 'multiple_choice', name='TypeEnum'), default="text", nullable=False)
    value = Column(String())
    project_code = Column(String())
    optional = Column(Boolean(), default=False)

    def __init__(self, manifest_id, name, type, value, project_code, optional):
        self.name = name
        self.type = type
        self.value = value
        self.project_code = project_code
        self.optional = optional
        self.manifest_id = manifest_id

    def to_dict(self):
        result = {}
        for field in ["id", "name", "type", "value", "project_code", "optional", "manifest_id"]:
            result[field] = getattr(self, field)
        result["type"] = result["type"].value
        return result

class DatasetVersionModel(Base):
    __tablename__ = 'dataset_version'
    __table_args__ = {"schema": ConfigClass.RDS_SCHEMA_DEFAULT}
    id = Column(Integer, unique=True, primary_key=True)
    dataset_code = Column(String())
    dataset_geid = Column(String())
    version = Column(String())
    created_by = Column(String())
    created_at = Column(DateTime())
    location = Column(String())
    notes = Column(String())

    def __init__(self, dataset_code, dataset_geid, version, created_by, created_at, location, notes):
        self.dataset_code = dataset_code
        self.dataset_geid = dataset_geid
        self.version = version
        self.created_by = created_by
        self.created_at = created_at
        self.location = location
        self.notes = notes

    def to_dict(self):
        result = {}
        for field in ["dataset_code", "dataset_geid", "version", "created_by", "created_at", "location", "notes"]:
            result[field] = getattr(self, field)
        result["type"] = result["type"].value
        return result


