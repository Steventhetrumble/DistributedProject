from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class ModelManager(Model):
    id = Column(Integer, primary_key=True)
    project_name= Column(String(100),unique=True, nullable=False)
    steps_per_iteration = Column(Integer)
    max_steps = Column(Integer)
    steps_complete = Column(Integer)
    Data_path = Column(String(100))
    Data_Size = Column(Integer)
    Data_Split_Size = Column(Integer)
    original_model_path = Column(String(100)) # needs to be keras format
    final_model_path = Column(String(100)) # needs to be keras format
    parameters =Column(String(300))

    def splits(self):
        splits = self.Data_Size / self.Data_Split_Size
        return splits

    def __repr__(self):
        return self.project_name

class DownloadQueueBuilder(Model):
    id = Column(Integer,primary_key=True)
    name = Column(String(50), unique=True, nullable=False)



class DownloadModelsQueue(Model):
    id = Column(Integer, primary_key=True)
    project_name = Column(String(100), nullable=False)
    current_iteration = Column(Integer, nullable = False)
    model_path = Column(String(100), nullable=False)
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
    model_path = Column(String(100), nullable=False)
    step = Column(Integer)

    def __repr__(self):
        return self.project_name



"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""
        
