import tensorflowjs as tfjs
from keras.models import load_model
import os

def convert_and_save(path):
    model = load_model(path)
    print(model.get_weights())
    tfjs.converters.save_keras_model(model,'./')
   

#model = tfjs.converters.load_keras_model("../upload/model.json")

#tfjs.converters.save_keras_model(model, 'tfjs_model_after_upload')


if __name__ == "__main__":
    convert_and_save('./trained_model.h5')
    print("hi")