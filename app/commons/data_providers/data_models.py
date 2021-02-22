from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
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


