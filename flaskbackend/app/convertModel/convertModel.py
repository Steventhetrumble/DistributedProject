import tensorflowjs as tfjs
from keras.models import load_model

model = load_model("../SaveModel/trained_model.h5")

tfjs.converters.save_keras_model(model, 'tfjs_target_dir')
