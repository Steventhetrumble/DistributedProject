import pandas as pd
from keras.models import Sequential, load_model
from keras.layers import *

training_data_df = pd.read_csv("../ScaledData/sales_data_training_scaled.csv")

X = training_data_df.drop('total_earnings', axis=1).values
Y = training_data_df[['total_earnings']].values

# Define the model
model = Sequential()
model.add(Dense(50, input_dim=9, activation='relu'))
model.add(Dense(100, activation='relu'))
model.add(Dense(50, activation='relu'))
model.add(Dense(1, activation='linear'))
model.compile(loss='mean_squared_error', optimizer='adam')

# Train the model
model.fit(
    X,
    Y,
    epochs=0,
    shuffle=True,
    verbose=2
)

# Load the separate test data set
test_data_df = pd.read_csv("../ScaledData/sales_data_testing_scaled.csv")

X_test = test_data_df.drop('total_earnings', axis=1).values
Y_test = test_data_df[['total_earnings']].values

test_error_rate = model.evaluate(X_test, Y_test, verbose=0)
print("The mean squared error (MSE) for the test data set is: {}".format(test_error_rate))

# Save the model to disk
model.save("trained_model.h5")

print("Model saved to disk.")

del model

model=load_model("trained_model.h5")

print(model.get_weights())
