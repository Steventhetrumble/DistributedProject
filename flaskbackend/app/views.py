from flask import render_template, request, send_from_directory
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, expose, BaseView, AppBuilder
from app import appbuilder, db
import pandas as pd


#    Create your Views::
class MyView(BaseView):
    route_base = "/myview"

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


