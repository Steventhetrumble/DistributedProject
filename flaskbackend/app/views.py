from flask import render_template, request, send_from_directory, redirect, url_for
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, expose, BaseView, AppBuilder
from flask_appbuilder.actions import action
import logging
#from models import ModelManager, DownloadModelsQueue, UploadModelsQueue
from app import appbuilder, db
#from app.models import ModelManager, DownloadModelsQueue, UploadModelsQueue
from werkzeug.utils import secure_filename
import pandas as pd
import os
import json
import inspect
import tensorflowjs as tfjs
from keras.models import load_model
from .models import ModelManager, DownloadModelsQueue, UploadModelsQueue



#    Create your Views::
class MyView(BaseView):
    route_base = "/myview"
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','bin'])

    @expose('/method1/<string:param1>')
    def method1(self, param1):
        # do something with param1
        # and return it
        if(param1 == "model"):
            return send_from_directory('./convertModel/tfjs_target_dir',"model.json")
            
        else:
            return send_from_directory('./convertModel/tfjs_target_dir', param1)

    @expose('/method2/')
    def method2(self):
        # do something with param1
        # and render it
        df = pd.read_csv("app/ScaledData/sales_data_training_scaled.csv")
        thing = df.to_json(orient='values')
        # index, columns, values, table
        return thing

    @expose('/method3/', methods = ['GET', 'POST'])
    def method3(self):
        if request.method == 'POST':          
            appbuilder.get_app.logger.info(request.files)
            for a_file in request.files:
                if a_file and self.allowed_file(a_file):
                    a_file_name = secure_filename(a_file)
                    a_file_target = os.path.join(appbuilder.get_app.config['UPLOAD_FOLDER'], a_file_name)
                    file = request.files[a_file]
                    file.save(a_file_target)
            return redirect(request.url)
        return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
            
    def allowed_file(self,filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

class ModelManagerView(ModelView):
    route_base = "/Model"
    datamodel = SQLAInterface(ModelManager, db.session)
    list_columns = ["project_name", "parameters", "steps_per_iteration", "max_steps", "steps_complete", "Data_path", "Data_Size","Data_Split_Size","original_model_path", "final_model_path","upload_Queue_path", "download_Queue_path"]
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','bin'])

    @expose("/list_models/")
    def list_models(self):
        session = self.datamodel.session()
        res = session.query(ModelManager.project_name).all()
        pre_result = str(res)
        result = "{" + pre_result + "}"
        return result
    
    def create_download_queue(self,project_name):
        session = self.datamodel.session()
        max_steps = session.query(ModelManager.max_steps).filter(ModelManager.project_name == project_name).first()
        data_size = session.query(ModelManager.Data_Size).filter(ModelManager.project_name == project_name).first()
        iterations = max_steps[0]/data_size[0]
        appbuilder.get_app.logger.info(str(iterations))
        data_split_size = session.query(ModelManager.Data_Split_Size).filter(ModelManager.project_name == project_name).first()
        task_number = data_size[0]/data_split_size[0]
        appbuilder.get_app.logger.info(str(task_number))
        Original_Path = session.query(ModelManager.original_model_path).filter(ModelManager.project_name == project_name).first()
        Download_Queue = session.query(ModelManager.download_Queue_path).filter(ModelManager.project_name == project_name).first()
        Upload_Queue = session.query(ModelManager.upload_Queue_path).filter(ModelManager.project_name == project_name)
        data_path = session.query(ModelManager.Data_path).filter(ModelManager.project_name == project_name).first()
        self.prepare_down_up_file_struct(Original_Path,Download_Queue, Upload_Queue, int(iterations), int(task_number), project_name, data_path )



        
    
    def prepare_down_up_file_struct(self,Original_Path, Download_Queue,Upload_Queue, iterations, splits, project_name, data_path):
        session = self.datamodel.session()
        model_name = "trained_model.h5"
        model = load_model(Original_Path+ "/Keras/" + model_name)
        # TODO: model name needs to be stored
        tfjs.converters.save_keras_model(model,Original_Path + "/web" )
        # TODO: Download queue folder structure is not required
        for i in range(iterations):
            for j in range(splits):
                if not os.path.exists(Download_Queue + "/" + str(i)):
                    os.mkdir( Download_Queue + "/" + str(i))
                if not os.path.exists(Upload_Queue + "/" + str(i)):
                    os.mkdir( Upload_Queue + "/" + str(i))
                if not os.path.exists( Upload_Queue + "/" + str(i) + "/" + str(j) ):
                    os.mkdir( Upload_Queue + "/" + str(i) + "/" + str(j) )
                if not os.path.exists( Download_Queue + "/" + str(i) + "/" + str(j) ):
                    os.mkdir( Download_Queue + "/" + str(i) + "/" + str(j) )
                if i == 0:
                    tfjs.converters.save_keras_model(model, Download_Queue + "/" + str(i) + "/" + str(j) )
                # TODO: finish automatically making these objects
                new_dqueue_member = DownloadModelsQueue(project_name =project_name,current_iteration =i,model_path =  Download_Queue + "/" + str(i) + "/" + str(j),data_path =data_path, step =1, step_size = 10, is_created =False, is_complete =False)
                new_uqueue_member = UploadModelsQueue()
                session.add(new_queue_member)
                session.commit()
    #      prepare_original("../static/Test_Project/Original/Keras/trained_model.h5",
    #  '../static/Test_Project/Original/web',"../static/Test_Project/Download_Queue",
    #  5, 5)

    @expose("/method1/<string:projects>")
    def method1(self, projects):
        session = self.datamodel.session()
        res = session.query(ModelManager.Data_Size).filter(ModelManager.project_name == projects).first()
        
        return str(res)

    @expose("/get_Model/<string:projects>/<string:filename>")
    def get_Model(self, projects, filename):
        session = self.datamodel.session()
        res = session.query(ModelManager.project_name).filter(ModelManager.project_name == projects).first()
        
        rest = str(res)
        
        if(rest == "None"):
            return redirect(request.url,404)
        
        else:
            
            if(filename == "model"):
                path = session.query(DownloadModelsQueue.model_path).filter(ModelManager.project_name == projects).first()
                if(str(path)== "None"):
                    self.create_download_queue(projects)
                return str(path)
                #return send_from_directory(session.query(DownloadModelsQueue.model_path).filter(ModelManager.project_name == projects).first(),"model.json")
                
            else:
                path = session.query(DownloadModelsQueue.model_path).filter(ModelManager.project_name == projects).first()
                return str(path)
                #return send_from_directory(session.query(DownloadModelsQueue.model_path).filter(ModelManager.project_name == projects).first(), filename)
            
        return str(res)


class DownloadModelsQueueView(ModelView):
    datamodel = SQLAInterface(DownloadModelsQueue, db.session)
    list_columns = ["project_name", "current_iteration", "model_path", "data_path", "step", "step_size", "is_created", "is_complete" ]
    route_base = "/myview"

class UploadModelsQueueView(ModelView):
    datamodel = SQLAInterface(UploadModelsQueue, db.session)
    list_columns = ["project_name", "current_iteration", "model_path","step"]
    route_base = "/myview2"
    @expose("/buildNextUploadQueue/")
    def buildNextUploadQueue(self):
        return redirect(self.get_redirect())

#    Next, register your Views::

appbuilder.add_view(ModelManagerView, "Model Manager", icon="fa-folder-open-o", category="Admin", category_icon='fa-envelope')
appbuilder.add_view(DownloadModelsQueueView, "Download Queue", icon="fa-folder-open-o", category="Admin")
appbuilder.add_view(UploadModelsQueueView, "Upload Queue", icon="fa-folder-open-o", category="Admin")


appbuilder.add_view_no_menu(MyView())
"""
    Application wide 404 error handler
"""
@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404

db.create_all()