import pandas as pd
from keras.models import Sequential
from keras.layers import Dense

training_data_df = pd.read_csv("ScaledData/sales_data_training_scaled.csv")

X = training_data_df.drop('total_earnings', axis=1).values
Y = training_data_df[['total_earnings']].values

# Define the model
model1 = Sequential()
model1.add(Dense(3, input_dim=9, activation='relu'))
model1.add(Dense(2, activation='relu'))
model1.add(Dense(1, activation='linear'))
model1.compile(loss='mean_squared_error', optimizer='adam')

# Train the model
model1.fit(
    X,
    Y,
    epochs=1,
    shuffle=True,
    verbose=2
)

# Load the separate test data set
test_data_df = pd.read_csv("ScaledData/sales_data_testing_scaled.csv")

X_test = test_data_df.drop('total_earnings', axis=1).values
Y_test = test_data_df[['total_earnings']].values

test_error_rate = model1.evaluate(X_test, Y_test, verbose=0)
print("The mean squared error (MSE) for the test data set is: {}".format(test_error_rate))

# Save the model to disk
model1.save("sampleModels/model1.h5")
print("Model saved to disk.")

model2 = Sequential()
model2.add(Dense(3, input_dim=9, activation='relu'))
model2.add(Dense(2, activation='relu'))
model2.add(Dense(1, activation='linear'))
model2.compile(loss='mean_squared_error', optimizer='adam')

# Train the model
model2.fit(
    X,
    Y,
    epochs=1,
    shuffle=True,
    verbose=2
)

# Load the separate test data set
test_data_df = pd.read_csv("ScaledData/sales_data_testing_scaled.csv")

X_test = test_data_df.drop('total_earnings', axis=1).values
Y_test = test_data_df[['total_earnings']].values

test_error_rate = model2.evaluate(X_test, Y_test, verbose=0)
print("The mean squared error (MSE) for the test data set is: {}".format(test_error_rate))

# Save the model to disk
model2.save("sampleModels/model2.h5")
print("Model saved to disk.")