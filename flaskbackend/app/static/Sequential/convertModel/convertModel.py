import tensorflowjs as tfjs
from keras.models import load_model
import os

def prepare_original(Original_Path_Keras, Original_Path_Web, Download_Queue, iterations, splits ):
    model = load_model(Original_Path_Keras)
    print(model.get_weights())
    tfjs.converters.save_keras_model(model,Original_Path_Web)
    for i in range(iterations):
        for j in range(splits):
            if not os.path.exists(Download_Queue + "/" + str(i)):
                os.mkdir( Download_Queue + "/" + str(i))
            if not os.path.exists( Download_Queue + "/" + str(i) + "/" + str(j) ):
                os.mkdir( Download_Queue + "/" + str(i) + "/" + str(j) )
            if i == 0:
                tfjs.converters.save_keras_model(model, Download_Queue + "/" + str(i) + "/" + str(j) )


#model = tfjs.converters.load_keras_model("../upload/model.json")

#tfjs.converters.save_keras_model(model, 'tfjs_model_after_upload')


if __name__ == "__main__":
    prepare_original("../static/Test_Project/Original/Keras/trained_model.h5",
     '../static/Test_Project/Original/web',"../static/Test_Project/Download_Queue",
     5, 5)