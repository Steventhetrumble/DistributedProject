from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship


class ModelManager(Model):
    # TODO: can replace all paths with one path and add endings in create download queue function
    id = Column(Integer, primary_key=True)
    project_name = Column(String(100), unique=True, nullable=False)
    steps_per_iteration = Column(Integer)
    max_steps = Column(Integer)
    steps_complete = Column(Integer, default=0)
    Data_Size = Column(Integer)
    Data_Split_Size = Column(Integer)
    label_index = Column(Integer)
    is_combining = Column(Boolean, default=False)

    def __repr__(self):
        return self.project_name


class DownloadModelsQueue(Model):
    id = Column(Integer, primary_key=True)
    project_name = Column(String(100), nullable=False)
    current_iteration = Column(Integer, nullable=False)
    model_path = Column(String(100), nullable=True)
    step = Column(Integer)
    step_size = Column(Integer)
    is_created = Column(Boolean, default=False)
    is_complete = Column(Boolean, default=False)
    is_checked_out = Column(Boolean, default=False)

    def __repr__(self):
        return self.project_name


class UploadModelsQueue(Model):
    id = Column(Integer, primary_key=True)
    project_name = Column(String(100), nullable=False)
    loss = Column(Float)
    current_iteration = Column(Integer, nullable=False)
    model_path = Column(String(100), nullable=False)
    step = Column(Integer)
    is_uploaded = Column(Boolean, default=False)

    def __repr__(self):
        return self.project_name


"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""
