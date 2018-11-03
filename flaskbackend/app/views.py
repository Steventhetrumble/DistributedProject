from flask import render_template, request, send_from_directory, flash, redirect, url_for
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, expose, BaseView, AppBuilder
import logging
from app import appbuilder, db
from werkzeug.utils import secure_filename
import pandas as pd
import os


#    Create your Views::
class MyView(BaseView):
    route_base = "/myview"
    UPLOAD_FOLDER = '/upload'
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
            #check if the post request has the file part
            # if 'file' not in request.files:
            #     flash('No file part')
            #     return redirect(request.url)
            for files in request.files:
                appbuilder.get_app.logger.info(files)
                
                if files and self.allowed_file(files):
                    file = request.files[files]
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(self.UPLOAD_FOLDER))
                    return redirect(url_for('uploaded_file', filename=filename))
            if 'file' not in request.files:
                flash('No file part')
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


    # class MyModelView(ModelView):
    #     datamodel = SQLAInterface(MyModel)


#    Next, register your Views::


    # appbuilder.add_view(MyModelView, "My View", icon="fa-folder-open-o", category="My Category", category_icon='fa-envelope')

appbuilder.add_view_no_menu(MyView())
"""
    Application wide 404 error handler
"""
@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404

db.create_all()


