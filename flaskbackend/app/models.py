from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class ModelManager(Model):
    id = Column(Integer, primary_key=True)
    project_name= Column(String(100),unique=True, nullable=False)
    #parameters =Column(String(1000), nullable=False)
    steps_per_iteration = Column(Integer)
    max_steps = Column(Integer)
    steps_complete = Column(Integer)
    Data_path = Column(String(100))
    Data_Size = Column(Integer)
    batch_size = Column(Integer)
    original_model_path = Column(String(100)) # needs to be keras format
    final_model_path = Column(String(100)) # needs to be keras format


    def __repr__(self):
        return self.project_name


class DownloadModelsQueue(Model):
    id = Column(Integer, primary_key=True)
    project_name = Column(String(100), nullable=False)
    current_iteration = Column(Integer, nullable = False)
    model_path = Column(FileColumn, nullable=False)
    data_path = Column(String(100))
    step = Column(Integer)
    step_size = Column(Integer)
    is_created = Column(Boolean,default=False)
    #is_uploaded = Column(Boolean,default=False)
    is_complete = Column(Boolean, default=False)
    
    def __repr__(self):
        return self.project_name

class UploadModelsQueue(Model):
    id = Column(Integer, primary_key=True )
    project_name = Column(String(100), unique = True, nullable=False)
    current_iteration = Column(Integer, nullable = False)
    model_path = Column(FileColumn, nullable=False)
    step = Column(Integer)

    def __repr__(self):
        return self.project_name


class testModel(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    def __repr__(self):
        return self.name


"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""
        
