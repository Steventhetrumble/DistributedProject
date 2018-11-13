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
    list_columns = ["project_name", "parameters", "steps_per_iteration", "max_steps", "steps_complete", "Data_path", "Data_Size","Data_Split_Size","original_model_path", "final_model_path"]
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','bin'])

    @expose("/list_models/")
    def list_models(self):
        session = self.datamodel.session()
        res = session.query(ModelManager.project_name).all()
        pre_result = str(res)
        result = "{" + pre_result + "}"
        return result



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
        appbuilder.get_app.logger.info(rest)
        if(rest == "None"):
            return redirect(request.url,404)
        
        else:
            
            if(filename == "model"):
                f = session.query(DownloadModelsQueue.model_path).filter(ModelManager.project_name == projects).first()
                return str(f)
                #return send_from_directory(session.query(DownloadModelsQueue.model_path).filter(ModelManager.project_name == projects).first(),"model.json")
                
            else:
                f = session.query(DownloadModelsQueue.model_path).filter(ModelManager.project_name == projects).first()
                return str(f)
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