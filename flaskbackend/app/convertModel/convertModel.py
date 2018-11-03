import tensorflowjs as tfjs
from keras.models import load_model

#model = load_model("../upload/model.json")
#tfjs.converters.save_keras_model(model, 'tfjs_target_dir')
model = tfjs.converters.load_keras_model("../upload/model.json")
print(model.get_weights())
tfjs.converters.save_keras_model(model, 'tfjs_model_after_upload')


