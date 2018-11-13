import pandas as pd
import numpy as np
from keras.models import Sequential, load_model, clone_model
from keras.layers import Dense

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

def print_layer_shapes(layer):
    for l in layer:
        print(l.shape)
        print(l[0])


model1 = load_model("sampleModels/model1.h5")
model2 = load_model("sampleModels/model2.h5")
models = []
models.append(model1)
models.append(model2)

out = average_combine(models)