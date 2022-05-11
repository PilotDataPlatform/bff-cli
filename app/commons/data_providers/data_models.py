# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.types import Enum

from .database import Base
from ...config import ConfigClass


class TypeEnum(Enum):
    text = 'text'
    multiple_choice = 'multiple_choice'


class DataManifestModel(Base):
    __tablename__ = 'data_manifest'
    __table_args__ = {'schema': ConfigClass.RDS_SCHEMA_DEFAULT}

    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String())
    project_code = Column(String())

    def __init__(self, name, project_code):
        self.name = name
        self.project_code = project_code

    def to_dict(self):
        result = {}
        for field in ['id', 'name', 'project_code']:
            result[field] = getattr(self, field)
        return result


class DataAttributeModel(Base):
    __tablename__ = 'data_attribute'
    __table_args__ = {'schema': ConfigClass.RDS_SCHEMA_DEFAULT}
    id = Column(Integer, unique=True, primary_key=True)
    manifest_id = Column(Integer, ForeignKey(DataManifestModel.id))
    name = Column(String())
    type = Column(
        Enum('text', 'multiple_choice', name='TypeEnum'),
        default='text',
        nullable=False)
    value = Column(String())
    project_code = Column(String())
    optional = Column(Boolean(), default=False)

    def __init__(
        self,
        manifest_id,
        name,
        attr_type,
        value,
        project_code,
        optional
    ):
        self.name = name
        self.type = attr_type
        self.value = value
        self.project_code = project_code
        self.optional = optional
        self.manifest_id = manifest_id

    def to_dict(self):
        result = {}
        expected_fields = [
            'id', 'name', 'type', 'value',
            'project_code', 'optional', 'manifest_id']
        for field in expected_fields:
            result[field] = getattr(self, field)
        result['type'] = result['type'].value
        return result


class DatasetVersionModel(Base):
    __tablename__ = 'dataset_version'
    __table_args__ = {'schema': ConfigClass.RDS_SCHEMA_DEFAULT}
    id = Column(Integer, unique=True, primary_key=True)
    dataset_code = Column(String())
    dataset_geid = Column(String())
    version = Column(String())
    created_by = Column(String())
    created_at = Column(DateTime())
    location = Column(String())
    notes = Column(String())

    def __init__(
        self,
        dataset_code,
        dataset_geid,
        version,
        created_by,
        created_at,
        location,
        notes
    ):
        self.dataset_code = dataset_code
        self.dataset_geid = dataset_geid
        self.version = version
        self.created_by = created_by
        self.created_at = created_at
        self.location = location
        self.notes = notes

    def to_dict(self):
        result = {}
        expected_fields = [
            'dataset_code', 'dataset_geid', 'version',
            'created_by', 'created_at', 'location',
            'notes']
        for field in expected_fields:
            result[field] = getattr(self, field)
        result['type'] = result['type'].value
        return result
