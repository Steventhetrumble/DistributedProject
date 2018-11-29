from flask import render_template, request, send_from_directory, redirect, url_for, jsonify
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, expose, BaseView, AppBuilder
from flask_appbuilder.actions import action
import logging
# from models import ModelManager, DownloadModelsQueue, UploadModelsQueue
from app import appbuilder, db
# from app.models import ModelManager, DownloadModelsQueue, UploadModelsQueue
from werkzeug.utils import secure_filename
import pandas as pd
import os
import shutil
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
import tensorflow as tf
from keras import backend as K


#    Create your Views::
class MyView(BaseView):
    route_base = "/Sequential"
    ALLOWED_EXTENSIONS = set(
        ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bin', 'json'])

    def test_threads(self):
        for _ in range(2):
            time.sleep(1)
            appbuilder.get_app.logger.info("hey how are you")

    @expose('/get_model/<string:model>')
    def get_model(self, model):
        # do something with model
        # and return it
        if(model == "model"):
            return send_from_directory('./static/Sequential/SaveModel', "model.json")
        else:
            return send_from_directory('./static/Sequential/SaveModel', model)

    @expose('/get_train_data')
    def get_training_data(self):
        threading.Thread(target=self.test_threads).start()
        df = pd.read_csv(
            "app/static/Sequential/ScaledData/sales_data_training_scaled.csv")
        thing = df.to_json(orient='values')
        # index, columns, values, table
        return thing

    @expose('/get_test_data')
    def get_testing_data(self):
        threading.Thread(target=self.test_threads).start()
        df = pd.read_csv(
            "app/static/Sequential/ScaledData/sales_data_testing_scaled.csv")
        thing = df.to_json(orient='values')
        # index, columns, values, table
        appbuilder.get_app.logger.info(thing)
        return thing

    @expose('/put_final_model', methods=['GET', 'POST'])
    def method3(self):
        if request.method == 'POST':
            appbuilder.get_app.logger.info(request.files)
            for a_file in request.files:
                if a_file and self.allowed_file(a_file):
                    a_file_name = secure_filename(a_file)
                    a_file_target = os.path.join(
                        appbuilder.get_app.config['UPLOAD_FOLDER'] + "Sequential/Final/up", a_file_name)
                    file = request.files[a_file]
                    file.save(a_file_target)

            sess = tf.Session()
            K.set_session(sess)
            model = get_keras_model(
                "./app/static/Sequential/Final/up/model.json")
            tfjs.converters.save_keras_model(
                model, "./app/static/Sequential/Final/converted")

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

    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    @expose("/get_final_model/<string:model>")
    def get_final_model(self, model):
        if(model == "model"):
            return send_from_directory('./static/Sequential/Final/converted', "model.json")
        else:
            return send_from_directory('./static/Sequential/Final/converted', model)


class ModelManagerView(ModelView):
    route_base = "/Parallel"
    datamodel = SQLAInterface(ModelManager, db.session)
    list_columns = ["project_name", "label_index", "steps_per_iteration",
                    "max_steps", "steps_complete", "Data_Size", "Data_Split_Size", "is_combining"]
    ALLOWED_EXTENSIONS = set(
        ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bin', 'json', '.h5'])

    add_columns = ["project_name", "steps_per_iteration",
                   "max_steps", "Data_Size", "Data_Split_Size", "label_index"]
    edit_columns = ["project_name", "steps_per_iteration", "max_steps",
                    "steps_complete", "Data_Size", "Data_Split_Size", "label_index"]

    @expose("/get_label_index/<string:project_name>")
    def get_label_index(self, project_name):
        session = self.datamodel.session()
        res = session.query(ModelManager.label_index).filter(
            ModelManager.project_name == project_name).first()
        return jsonify(res)

    @expose("/list_models/")
    def list_models(self):
        session = self.datamodel.session()
        res = session.query(ModelManager.project_name).all()
        projects = []
        for r in res:
            projects.append(r[0])
        return jsonify(projects)

    @expose("/create_download_queue/<string:project_name>")
    def create_download_queue(self, project_name):

        session = self.datamodel.session()
        res = session.query(ModelManager).filter(
            ModelManager.project_name == project_name).first()
        max_steps = res.max_steps
        data_size = res.Data_Size
        iterations = max_steps/data_size
        data_split_size = res.Data_Split_Size
        task_number = data_size/data_split_size
        self.prepare_down_up_file_struct(int(iterations), int(
            task_number), project_name, int(data_split_size), int(data_size))
        return "complete"

    def prepare_down_up_file_struct(self, iterations, splits, project_name, data_split_size, data_size):
        session = self.datamodel.session()
        model_name = "trained_model.h5"
        model = load_model("./app/static/" + project_name +
                           "/Original/Keras/" + model_name)
        # TODO: model name needs to be stored
        tfjs.converters.save_keras_model(
            model, "./app/static/" + project_name+"/Original/web")

        session.query(DownloadModelsQueue).filter(
            DownloadModelsQueue.project_name == project_name).delete()
        session.query(UploadModelsQueue).filter(
            UploadModelsQueue.project_name == project_name).delete()

        for i in range(iterations):
            download_base_url = "./app/static/{}/Download_Queue/{}".format(
                project_name, i)
            upload_base_url = "./app/static/{}/Upload_Queue/{}".format(
                project_name, i)

            # Remove directory and files from previous run
            if os.path.exists(download_base_url):
                shutil.rmtree("{}".format(download_base_url))

            # Remove directory and files from previous run
            if os.path.exists(upload_base_url):
                shutil.rmtree("{}".format(upload_base_url))

            if not os.path.exists(download_base_url):
                os.mkdir(download_base_url)

            if not os.path.exists(upload_base_url):
                os.mkdir(upload_base_url)

            for j in range(splits):
                is_created = False
                # if not os.path.exists("./app/static/" + project_name + "/Original/web/"+str(i)):
                #     os.mkdir("./app/static/" + project_name + "/Original/web/"+str(i))

                if not os.path.exists("{}/{}".format(upload_base_url, j)):
                    os.mkdir("{}/{}".format(upload_base_url, j))

                if not os.path.exists("{}/{}".format(download_base_url, j)):
                    os.mkdir("{}/{}".format(download_base_url, j))

                if i == 0:
                    tfjs.converters.save_keras_model(
                        model, "{}/{}".format(download_base_url, j))
                    is_created = True

                new_dqueue_member = DownloadModelsQueue(project_name=project_name, current_iteration=i, model_path="{}/{}".format(
                    i, j), step=i*data_size + j*data_split_size, step_size=data_split_size, is_created=is_created)
                new_uqueue_member = UploadModelsQueue(
                    project_name=project_name, loss=None, current_iteration=i, model_path="{}/{}".format(i, j), step=i*data_size + j*data_split_size)
                session.add(new_dqueue_member)
                session.add(new_uqueue_member)
                session.commit()

    @expose("/method1/<string:projects>")
    def method1(self, projects):
        session = self.datamodel.session()
        res = session.query(ModelManager.Data_Size).filter(
            ModelManager.project_name == projects).first()

        return str(res)

    @expose("/get_data/<string:project>/<int:iteration>/<int:task_number>")
    def get_data(self, project, iteration, task_number):
        path = str(iteration) + "/" + str(task_number)
        data_name = "training_data.csv"
        session = self.datamodel.session()
        res = session.query(DownloadModelsQueue).filter(and_(
            DownloadModelsQueue.project_name == project, DownloadModelsQueue.model_path == path)).first()
        df = pd.read_csv(
            "app/static/" + str(res.project_name)+"/Data/" + data_name)
        df = df.loc[task_number*res.step_size:task_number *
                    res.step_size + res.step_size, :]
        thing = df.to_json(orient='values')
        # index, columns, values, table
        return thing

    @expose("/get_test_data/<string:project>")
    def get_test_data(self, project):
        data_name = "testing_data.csv"
        df = pd.read_csv(
            "app/static/{}/Data/{}".format(project, data_name))
        thing = df.to_json(orient='values')
        # index, columns, values, table
        return thing

    @expose("/get_loss/<string:project>")
    def get_loss(self, project):
        session = self.datamodel.session()
        res = session.query(UploadModelsQueue.loss).filter(and_(
            UploadModelsQueue.project_name == project)).all()

        loss = []
        for index, r in enumerate(res):
            if r[0] is not None:
                loss.append([index, r])

        return jsonify(loss)

    @expose("/check_model_for_down/<string:project>")
    def check_model_for_down(self, project):
        session = self.datamodel.session()
        res = session.query(ModelManager).filter(
            ModelManager.project_name == project).first()
        rest = str(res.project_name)
        if(rest == "None"):
            return redirect(request.url, 404)
        else:
            path = self.check_dq(res.project_name)
            return jsonify({'result': path})

    def check_model_for_up(self, project, iteration, task_number):
        path = iteration + "/" + task_number
        session = self.datamodel.session()
        res = session.query(ModelManager).filter(
            ModelManager.project_name == project).first()
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
            return send_from_directory("./static/" + project + "/Download_Queue/" + path, "model.json")
        else:
            return send_from_directory("./static/" + project + "/Download_Queue/" + path, filename)

    @expose("/get_final_model/<string:project>/<string:filename>")
    def get_final_model(self, project, filename):
        if(filename == "model"):
            return send_from_directory("./static/{}/Final".format(project), "model.json")
        else:
            return send_from_directory("./static/{}/Final".format(project), filename)

    def check_uq(self, project, path):
        session = self.datamodel.session()
        res = session.query(UploadModelsQueue).filter(and_(
            UploadModelsQueue.project_name == project, UploadModelsQueue.model_path == path)).first()
        return res.is_uploaded

    def check_dq(self, project):
        session = self.datamodel.session()
        if(self.check_if_complete(project)):
            return "done"
        if(self.check_if_combining(project)):
            return "wait"
        if(self.check_if_checked_out(project)):
            res = session.query(DownloadModelsQueue).filter(and_(DownloadModelsQueue.project_name == project,
                                                                 DownloadModelsQueue.is_complete == False, DownloadModelsQueue.is_created == True)).first()
            return res.model_path
        else:
            res = session.query(DownloadModelsQueue).filter(and_(DownloadModelsQueue.project_name == project, DownloadModelsQueue.is_complete ==
                                                                 False, DownloadModelsQueue.is_created == True, DownloadModelsQueue.is_checked_out == False)).first()
            res.is_checked_out = True
            session.commit()
            return res.model_path

    def check_if_complete(self, project):
        session = self.datamodel.session()
        res = session.query(DownloadModelsQueue).filter(and_(
            DownloadModelsQueue.project_name == project, DownloadModelsQueue.is_complete == False)).all()
        if(len(res) == 0):
            return True
        else:
            return False

    def check_if_combining(self, project):
        session = self.datamodel.session()
        res = session.query(DownloadModelsQueue).filter(and_(DownloadModelsQueue.project_name == project,
                                                             DownloadModelsQueue.is_complete == False, DownloadModelsQueue.is_created == True)).all()
        if(len(res) == 0):
            return True
        else:
            return False

    def check_if_checked_out(self, project):
        session = self.datamodel.session()
        res = session.query(DownloadModelsQueue).filter(and_(DownloadModelsQueue.project_name == project, DownloadModelsQueue.is_complete ==
                                                             False, DownloadModelsQueue.is_created == True, DownloadModelsQueue.is_checked_out == False)).all()
        if(len(res) == 0):
            return True
        else:
            return False

    def check_if_iteration_is_complete(self, project):
        session = self.datamodel.session()
        model_manager = session.query(ModelManager).filter(
            ModelManager.project_name == project).first()
        current_iteration = model_manager.steps_complete / \
            model_manager.steps_per_iteration
        res = session.query(UploadModelsQueue).filter(and_(UploadModelsQueue.project_name == project,
                                                           UploadModelsQueue.current_iteration == current_iteration, UploadModelsQueue.is_uploaded == False)).all()
        if(len(res) == 0):
            return True
        else:
            return False

    def check_and_combine(self, project):
        session = self.datamodel.session()
        model_manager = session.query(ModelManager).filter(
            ModelManager.project_name == project).first()

        appbuilder.get_app.logger.info(project)
        if self.check_if_iteration_is_complete(project) and not model_manager.is_combining:
            model_manager.is_combining = True
            session.commit()
            self.combine_model(project)
            model_manager.is_combining = False
            session.commit()

    @expose('/put_model/<string:project>/<string:iteration>/<string:task_number>/<string:loss>', methods=['GET', 'POST'])
    def put_model(self, project, iteration, task_number, loss):
        path = iteration + "/" + task_number

        session = self.datamodel.session()
        download_models_queue = session.query(DownloadModelsQueue).filter(and_(
            DownloadModelsQueue.project_name == project, DownloadModelsQueue.model_path == path)).first()
        upload_models_queue = session.query(UploadModelsQueue).filter(and_(
            UploadModelsQueue.project_name == project, UploadModelsQueue.model_path == path)).first()

        if request.method == 'POST':
            appbuilder.get_app.logger.info(request.files)
            for a_file in request.files:
                if a_file and self.allowed_file(a_file):
                    a_file_name = secure_filename(a_file)
                    a_file_target = os.path.join(
                        appbuilder.get_app.config['UPLOAD_FOLDER'] + "/" + upload_models_queue.project_name + "/Upload_Queue/" + upload_models_queue.model_path, a_file_name)
                    file = request.files[a_file]
                    file.save(a_file_target)
            download_models_queue.is_complete = True
            download_models_queue.is_checked_out = False
            upload_models_queue.is_uploaded = True
            upload_models_queue.loss = float(loss)
            session.commit()
            # threading.Thread(target=self.check_and_combine,
            #                  args=(project,)).start()
            self.check_and_combine(project)
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

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def combine_model(self, project):
        session = self.datamodel.session()
        model_manager = session.query(ModelManager).filter(
            ModelManager.project_name == project).first()
        max_steps = model_manager.max_steps

        data_size = model_manager.Data_Size
        appbuilder.get_app.logger.info(data_size)

        data_split_size = model_manager.Data_Split_Size
        appbuilder.get_app.logger.info(data_split_size)
        task_number = data_size / data_split_size
        current_iteration = model_manager.steps_complete / \
            model_manager.steps_per_iteration
        appbuilder.get_app.logger.info(task_number)
        models = []
        sess = tf.Session()
        K.set_session(sess)
        for i in range(int(task_number)):
            appbuilder.get_app.logger.info(i)
            path = "./app/static/{}/Upload_Queue/{}/{}/model.json".format(
                project, int(current_iteration), i)
            # path = "./app/static/" + project + "/Upload_Queue/" + \
            #     str(int(current_iteration)) + "/" + str(i) + "/model.json"

            models.append(get_keras_model(path))

        out_model = average_combine(models)
        appbuilder.get_app.logger.info(out_model.get_weights())

        model_manager.steps_complete += model_manager.steps_per_iteration
        session.commit()

        model_manager = session.query(ModelManager).filter(
            ModelManager.project_name == project).first()
        if(model_manager.steps_complete == model_manager.max_steps):
            tfjs.converters.save_keras_model(
                out_model, "./app/static/" + project + "/Final")
        else:
            current_iteration = model_manager.steps_complete / \
                model_manager.steps_per_iteration
            download_queue = session.query(DownloadModelsQueue).filter(and_(
                DownloadModelsQueue.project_name == project, DownloadModelsQueue.current_iteration == current_iteration)).all()
            for task in download_queue:
                path = "./app/static/" + project + "/Download_Queue/" + task.model_path
                appbuilder.get_app.logger.info(path)
                tfjs.converters.save_keras_model(out_model, path)
                task.is_created = True
                session.commit()
        del out_model

    @action("create_project", "Create project directory", "Create?", "fa-rocket", single=True)
    def create_project(self, items):
        if not os.path.exists("./app/static/{}/Data".format(items[0].project_name)):
            os.makedirs(
                "./app/static/{}/Data".format(items[0].project_name), exist_ok=True)

        if not os.path.exists("./app/static/{}/Download_Queue".format(items[0].project_name)):
            os.makedirs(
                "./app/static/{}/Download_Queue".format(items[0].project_name), exist_ok=True)

        if not os.path.exists("./app/static/{}/Upload_Queue".format(items[0].project_name)):
            os.makedirs(
                "./app/static/{}/Upload_Queue".format(items[0].project_name), exist_ok=True)

        final_url = "./app/static/{}/Final".format(
            items[0].project_name)

        # Remove final files
        if os.path.exists(final_url):
            shutil.rmtree(final_url)

        if not os.path.exists(final_url):
            os.makedirs(
                final_url, exist_ok=True)

        if not os.path.exists("./app/static/{}/Original/Keras".format(items[0].project_name)):
            os.makedirs(
                "./app/static/{}/Original/Keras".format(items[0].project_name), exist_ok=True)

        if not os.path.exists("./app/static/{}/Original/web".format(items[0].project_name)):
            os.makedirs(
                "./app/static/{}/Original/web".format(items[0].project_name), exist_ok=True)

        self.update_redirect()
        return redirect("/Parallel/upload_original_model/{}".format(items[0].project_name))

    @expose('/upload_original_model/<string:project>', methods=['GET', 'POST'])
    def upload_original_model(self, project):
        if request.method == 'POST':
            appbuilder.get_app.logger.info(request.files)
            for a_file in request.files:
                if a_file:
                    a_file_target = os.path.join(
                        "{}/{}/Original/Keras".format(appbuilder.get_app.config['UPLOAD_FOLDER'], project), "trained_model.h5")
                    file = request.files[a_file]
                    file.save(a_file_target)
            return redirect("/Parallel/upload_training_data/{}".format(project))
        return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload Keras Model</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

    @expose('/upload_training_data/<string:project>', methods=['GET', 'POST'])
    def upload_training_data_model(self, project):
        if request.method == 'POST':
            appbuilder.get_app.logger.info(request.files)
            for a_file in request.files:
                if a_file:
                    a_file_target = os.path.join(
                        "{}/{}/Data".format(appbuilder.get_app.config['UPLOAD_FOLDER'], project), "training_data.csv")
                    file = request.files[a_file]
                    file.save(a_file_target)
            return redirect("/Parallel/upload_testing_data/{}".format(project))
        return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload Training Data</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

    @expose('/upload_testing_data/<string:project>', methods=['GET', 'POST'])
    def upload_testing_data(self, project):
        if request.method == 'POST':
            appbuilder.get_app.logger.info(request.files)
            for a_file in request.files:
                if a_file:
                    a_file_target = os.path.join(
                        "{}/{}/Data".format(appbuilder.get_app.config['UPLOAD_FOLDER'], project), "testing_data.csv")
                    file = request.files[a_file]
                    file.save(a_file_target)
            return redirect("/Parallel/create_download_queue/{}".format(project))
        return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload Testing Data</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


class DownloadModelsQueueView(ModelView):
    datamodel = SQLAInterface(DownloadModelsQueue, db.session)
    list_columns = ["project_name", "current_iteration", "model_path",
                    "step", "step_size", "is_created", "is_complete", "is_checked_out"]
    route_base = "/DownloadQueue"

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket", single=False)
    def muldelete(self, items):
        self.datamodel.delete_all(items)
        self.update_redirect()
        return redirect(self.get_redirect())


class UploadModelsQueueView(ModelView):
    datamodel = SQLAInterface(UploadModelsQueue, db.session)
    list_columns = ["project_name", "loss", "current_iteration",
                    "model_path", "step", "is_uploaded"]
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


appbuilder.add_view(ModelManagerView, "Model Manager",
                    icon="fa-folder-open-o", category="Admin", category_icon='fa-envelope')
appbuilder.add_view(DownloadModelsQueueView, "Download Queue",
                    icon="fa-folder-open-o", category="Admin")
appbuilder.add_view(UploadModelsQueueView, "Upload Queue",
                    icon="fa-folder-open-o", category="Admin")


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

# appbuilder.get_app.logger.info(request.files)


def get_keras_model(path):
    return tfjs.converters.load_keras_model(path, use_unique_name_scope=True)
