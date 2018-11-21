from flask import render_template, request, send_from_directory, redirect, url_for, jsonify
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
from keras.models import load_model, Sequential, clone_model
from keras.layers import Dense
from .models import ModelManager, DownloadModelsQueue, UploadModelsQueue
from sqlalchemy import and_, or_
import numpy as np
import threading
import time



#    Create your Views::
class MyView(BaseView):
    route_base = "/Sequential"
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','bin','json'])

    def test_threads(self):
        for i in range(2):
            time.sleep(1)
            appbuilder.get_app.logger.info("hey how are you")


    @expose('/method1/<string:param1>')
    def method1(self, param1):
        # do something with param1
        # and return it
        if(param1 == "model"):
            return send_from_directory('./static/Sequential/SaveModel',"model.json")
            
        else:
            return send_from_directory('./static/Sequential/SaveModel', param1)

    @expose('/method2/')
    def method2(self):
        # do something with param1
        # and render it
        threading.Thread(target=self.test_threads).start()
        df = pd.read_csv("app/static/Sequential/ScaledData/sales_data_training_scaled.csv")
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
                    a_file_target = os.path.join(appbuilder.get_app.config['UPLOAD_FOLDER'] + "/Sequential/upload", a_file_name)
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
    route_base = "/Parallel"
    datamodel = SQLAInterface(ModelManager, db.session)
    list_columns = ["project_name", "parameters", "steps_per_iteration", "max_steps", "steps_complete", "Data_Size","Data_Split_Size"]
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','bin','json'])

    @expose("/list_models/")
    def list_models(self):
        session = self.datamodel.session()
        res = session.query(ModelManager.project_name).all()
        pre_result = str(res)
        result = "{" + pre_result + "}"
        return result
    
    @expose("/create_download_queue/<string:project_name>")
    def create_download_queue(self,project_name):

        session = self.datamodel.session()
        res = session.query(ModelManager).filter(ModelManager.project_name == project_name).first()
        max_steps = res.max_steps
        data_size = res.Data_Size
        iterations = max_steps/data_size
        data_split_size = res.Data_Split_Size
        task_number = data_size/data_split_size
        self.prepare_down_up_file_struct(int(iterations), int(task_number), project_name, int(data_split_size), int(data_size))
        return "complete"
    
    def prepare_down_up_file_struct(self, iterations, splits, project_name, data_split_size, data_size):
        session = self.datamodel.session()
        model_name = "trained_model.h5"
        model = load_model("./app/static/" + project_name + "/Original/Keras/" + model_name)
        # TODO: model name needs to be stored
        tfjs.converters.save_keras_model(model,"./app/static/" + project_name+"/Original/web" )
        # TODO: Download queue folder structure is not required
        for i in range(iterations):
            for j in range(splits):
                is_created = False
                # if not os.path.exists("./app/static/" + project_name + "/Original/web/"+str(i)):
                #     os.mkdir("./app/static/" + project_name + "/Original/web/"+str(i))

                if not os.path.exists("./app/static/" + project_name + "/Download_Queue/" + str(i)):
                    os.mkdir("./app/static/" + project_name + "/Download_Queue/" + str(i))
                
                if not os.path.exists("./app/static/" + project_name + "/Upload_Queue/" + str(i)):
                    os.mkdir("./app/static/" + project_name + "/Upload_Queue/" + str(i))
                
                if not os.path.exists( "./app/static/" + project_name + "/Upload_Queue/"  + str(i) + "/" + str(j) ):
                    os.mkdir("./app/static/" + project_name + "/Upload_Queue/"  + str(i) + "/" + str(j) )
                
                if not os.path.exists("./app/static/" + project_name + "/Download_Queue/" + str(i) + "/" + str(j) ):
                    os.mkdir("./app/static/" + project_name + "/Download_Queue/" + str(i) + "/" + str(j) )
                
                if i == 0:
                    tfjs.converters.save_keras_model(model,"./app/static/" + project_name + "/Download_Queue/"+ str(i) + "/" + str(j) )
                    is_created = True

                new_dqueue_member = DownloadModelsQueue(project_name =project_name,current_iteration =i,model_path =  str(i) + "/" + str(j), step =i*data_size + j*data_split_size, step_size = data_split_size, is_created=is_created)
                new_uqueue_member = UploadModelsQueue(project_name =project_name, current_iteration = i , model_path = str(i) + "/" + str(j), step = i*data_size +j*data_split_size)
                session.add(new_dqueue_member)
                session.add(new_uqueue_member)
                session.commit()
  
    @expose("/method1/<string:projects>")
    def method1(self, projects):
        session = self.datamodel.session()
        res = session.query(ModelManager.Data_Size).filter(ModelManager.project_name == projects).first()
        
        return str(res)

    @expose("/get_data/<string:project>/<int:iteration>/<int:task_number>")
    def get_data(self, project, iteration, task_number):
        path = str(iteration) + "/" + str(task_number)
        data_name ="sales_data_training_scaled.csv"
        session = self.datamodel.session()
        res = session.query(DownloadModelsQueue).filter(and_( DownloadModelsQueue.project_name == project, DownloadModelsQueue.model_path == path)).first()
        df = pd.read_csv("app/static/" + str(res.project_name)+"/Data/" + data_name)
        df = df.loc[task_number*res.step_size:task_number*res.step_size + res.step_size,:]
        thing = df.to_json(orient='values')
        # index, columns, values, table
        return thing

    @expose("/check_model_for_down/<string:project>")
    def check_model_for_down(self, project):
        session = self.datamodel.session()
        res = session.query(ModelManager).filter(ModelManager.project_name == project).first()
        rest = str(res.project_name)
        if(rest == "None"):
            return redirect(request.url, 404)
        else:
            path = self.check_dq(res.project_name)
            return jsonify({'result':path})

    
    @expose("/check_model_for_up/<string:project>/<string:iteration>/<string:task_number>")
    def check_model_for_up(self, project, iteration, task_number):
        path = iteration + "/" + task_number
        session = self.datamodel.session()
        res = session.query(ModelManager).filter(ModelManager.project_name == project).first()
        rest = str(res.project_name)
        if(rest == "None"):
            return redirect(request.url, 404)
        else:
            result = self.check_uq(project, path)
            return "{'result':" + result + "}"

    @expose("/get_Model/<string:project>/<string:iteration>/<string:task_number>/<string:filename>")
    def get_Model(self, project, iteration, task_number, filename):       
        path = iteration + "/" + task_number
        if(filename == "model"):                
            return send_from_directory("./static/" + project + "/Download_Queue/" + path,"model.json")
        else:
            return send_from_directory("./static/" + project + "/Download_Queue/" + path, filename)   
        

    def check_uq(self, project, path):
        session = self.datamodel.session()
        res = session.query(UploadModelsQueue).filter(and_(UploadModelsQueue.project_name == project, UploadModelsQueue.model_path == path)).first()
        if(res.is_uploaded == False):
            return "ok"
        else:
            return ""
    
    def check_dq(self, project):
        session = self.datamodel.session()
        if(self.check_if_complete(project)):
            return "done"
        if(self.check_if_combining(project)):
            return "wait"
        if(self.check_if_checked_out(project)):
            res = session.query(DownloadModelsQueue).filter(and_(DownloadModelsQueue.project_name == project, DownloadModelsQueue.is_complete == False, DownloadModelsQueue.is_created == True)).first()
            return res.model_path
        else:
            res = session.query(DownloadModelsQueue).filter(and_(DownloadModelsQueue.project_name == project, DownloadModelsQueue.is_complete == False, DownloadModelsQueue.is_created == True, DownloadModelsQueue.is_checked_out == False)).first()
            res.is_checked_out = True
            session.commit()
            return res.model_path
    
    def check_if_complete(self, project):
        session = self.datamodel.session()
        res = session.query(DownloadModelsQueue).filter(and_(DownloadModelsQueue.project_name == project, DownloadModelsQueue.is_complete == False)).all()
        if(len(res)== 0):
            return True
        else:
            return False

    def check_if_combining(self, project):
        session = self.datamodel.session()
        res = session.query(DownloadModelsQueue).filter(and_(DownloadModelsQueue.project_name == project, DownloadModelsQueue.is_complete == False, DownloadModelsQueue.is_created == True)).all()
        if(len(res)== 0):
            return True
        else:
            return False

    def check_if_checked_out(self, project):
        session = self.datamodel.session()
        res = session.query(DownloadModelsQueue).filter(and_(DownloadModelsQueue.project_name == project, DownloadModelsQueue.is_complete == False, DownloadModelsQueue.is_created == True, DownloadModelsQueue.is_checked_out == False)).all()
        if(len(res)== 0):
            return True
        else:
            return False

    def check_if_iteration_is_complete(self, project):
        session = self.datamodel.session()
        model_manager = session.query(ModelManager).filter(ModelManager.project_name == project).first()
        current_iteration = model_manager.steps_complete / model_manager.steps_per_iteration
        res = session.query(UploadModelsQueue).filter(and_(UploadModelsQueue.project_name == project, UploadModelsQueue.current_iteration== current_iteration, UploadModelsQueue.is_uploaded == False)).all()
        if(len(res)== 0):
            return True
        else:
            return False
    
    def check_and_combine(self, project):
        appbuilder.get_app.logger.info(project)
        if(self.check_if_iteration_is_complete(project)):
            
            self.combine_model(project)
    

    
    @expose('/put_model/<string:project>/<string:iteration>/<string:task_number>', methods = ['GET', 'POST'])
    def put_model(self, project, iteration, task_number):
        path = iteration + "/" + task_number
        session = self.datamodel.session()
        download_models_queue = session.query(DownloadModelsQueue).filter(and_(DownloadModelsQueue.project_name == project, DownloadModelsQueue.model_path == path)).first()
        upload_models_queue = session.query(UploadModelsQueue).filter(and_(UploadModelsQueue.project_name ==  project, UploadModelsQueue.model_path == path)).first()
        
        if request.method == 'POST':          
            appbuilder.get_app.logger.info(request.files)
            for a_file in request.files:
                if a_file and self.allowed_file(a_file):
                    a_file_name = secure_filename(a_file)
                    a_file_target = os.path.join(appbuilder.get_app.config['UPLOAD_FOLDER'] + "/" + upload_models_queue.project_name + "/Upload_Queue/" + upload_models_queue.model_path, a_file_name)
                    file = request.files[a_file]
                    file.save(a_file_target)
            download_models_queue.is_complete = True
            download_models_queue.is_checked_out = False
            upload_models_queue.is_uploaded = True 
            session.commit()
            threading.Thread(target=self.check_and_combine, args=(project,)).start()
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

    def combine_model(self, project):
        session = self.datamodel.session()
        model_manager = session.query(ModelManager).filter(ModelManager.project_name == project).first()
        max_steps = model_manager.max_steps

        data_size = model_manager.Data_Size
        appbuilder.get_app.logger.info(data_size)

        iterations = max_steps/data_size

        data_split_size = model_manager.Data_Split_Size
        appbuilder.get_app.logger.info(data_split_size)
        task_number = data_size / data_split_size
        current_iteration = model_manager.steps_complete / model_manager.steps_per_iteration
        appbuilder.get_app.logger.info(task_number)
        models = []
        for i in range(int(task_number)):
            appbuilder.get_app.logger.info(i)
            path = "./app/static/"+ project + "/Upload_Queue/" + str(int(current_iteration)) + "/" + str(i) + "/model.json"
            model = tfjs.converters.load_keras_model(path)
            models.append(model)

        out_model = average_combine(models)

        model_manager.steps_complete += model_manager.steps_per_iteration
        session.commit()

        model_manager = session.query(ModelManager).filter(ModelManager.project_name == project).first()
        if(model_manager.steps_complete == model_manager.max_steps):
            tfjs.converters.save_keras_model(out_model,"./app/static/" + project + "/Final")
        else:    
            current_iteration = model_manager.steps_complete / model_manager.steps_per_iteration
            download_queue = session.query(DownloadModelsQueue).filter(and_(DownloadModelsQueue.project_name == project, DownloadModelsQueue.current_iteration == current_iteration)).all()
            for task in download_queue:
                path ="./app/static/Download_Queue/" + task.model_path
                tfjs.converters.save_keras_model(out_model, path)
            



class DownloadModelsQueueView(ModelView):
    datamodel = SQLAInterface(DownloadModelsQueue, db.session)
    list_columns = ["project_name", "current_iteration", "model_path", "step", "step_size", "is_created", "is_complete", "is_checked_out" ]
    route_base = "/DownloadQueue"
    
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket", single=False)
    def muldelete(self, items):
        self.datamodel.delete_all(items)
        self.update_redirect()
        return redirect(self.get_redirect())


class UploadModelsQueueView(ModelView):
    datamodel = SQLAInterface(UploadModelsQueue, db.session)
    list_columns = ["project_name", "current_iteration", "model_path","step", "is_uploaded"]
    route_base = "/myview2"

    @expose("/buildNextUploadQueue/")
    def buildNextUploadQueue(self):
        return redirect(self.get_redirect())

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket", single=False)
    def muldelete(self, items):
        self.datamodel.delete_all(items)
        self.update_redirect()
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



def average_combine(model_list):
    output_model = clone_model(model_list[0])

    for layer in enumerate(model_list[0].layers):
        # retrieve weights for the layer from the first model in the list
        layer_index = layer[0]
        layer_w = layer[1].get_weights()
        for model in enumerate(model_list[1:]):
            layer_w = np.add(layer_w, 
                            model[1].layers[layer_index].get_weights())
        layer_w = np.divide(layer_w, len(model_list))
        output_model.layers[layer_index].set_weights(layer_w)

    return output_model

#appbuilder.get_app.logger.info(request.files)
