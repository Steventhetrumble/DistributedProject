# Distributed Project

Distributed NN Training

## Dependencies

### Backend

1. Python 3.x 64-bit
1. pip
1. venv

### Frontend

1. NodeJS (v. 10.x)

## Details

# Backend

## Install

Dependencies: Python 3.5.x 64-bit, venv, pip

Windows
```
python -m venv venv
. venv/Scripts/activate.bat
pip install -r requirements.txt
```

Mac/Linux
```
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

NOTE: Linux users may need to use `python3` instead of `python`
NOTE: If installing fails due to tensorflow, ensure you are using python 3.5.x in 64-bit (3.6 64-bit should also work)

Setup admin account and database

```
fabmanager create-db
fabmanager create-admin
```

Follow the prompts to create the admin account (values can be anything, but remember username and password)

NOTE: If credentials are forgotten, another admin account can be created as long as the username and email are unique.
Alternatively, delete the `app.db` file and run `fabmanager create-db` command again, followed by `fabmanager create-admin`.

## Run

Start the server

```
fabmanager run
```

Setup Test Project

1. Goto http://localhost:8080
1. Click login in top right
1. Login using admin account createed previously
1. Click Admin dropdown in navbar and select Model Manager
1. Click '+' on the left side of the List Model Manager card
1. Enter the following

   - Project Name: Test_Project
   - Steps per Iteration: 1000
   - Max Steps: 20000
   - Data Size: 1000
   - Data Split Size: 200
   - Label Index: 8

1. Click Save
1. Terminate the server and run it again
1. Click the checkbox beside the new model entry
1. Click the action dropdown and select 'Create Project Directory'
1. For the Model, click 'choose file and choose 'trained_model.h5' located in SampleData&Model in the flaskbackend directory.
   - NOTE: the h5 file is a saved Keras model, defining model structure and possible starting weights
1. Click upload
1. For the Training data, click 'choose file' and choose 'training_data.csv' located in SampleData&Model in the flaskbackend directory.
1. Click upload
1. For the Testing data, click 'choose file' and choose 'testing_data.csv' located in SampleData&Model in the flaskbackend directory.
1. Click upload
1. Wait for 'complete' to appear on the screen.

Backend is now ready to serve tasks to the client


# Frontend

## Install (Requires NodeJS to be installed)

```
npm install
```

## Run

```
npm start
```

## Pages

### Home

Project selection (will say no projects if backend not running, or no projects in backend)

### Sequential

Clicking on "Start Training Model" Will cause the model to be trained sequentially for the set number of epochs

### Parallel

Clicking on "Start Training Model" will call the backend for the next task, then the task will be trained and the resulting model sent to backend. Graph shows the loss for each task throughout the training process (all workers, not just current worker). Iteration #, task #, and progress (%) is shown above the graph. Clicking "Evaluate" goes to the Evaluate page

### Evaluate

Gets the final model from the backend as well as the testing data. Once "Start Testing Model" is clicked, the testing data is used on the final model to get the Mean Square Error (MSE) for each test data entry, as well as the overall MSE. The individual MSE values are shown in the graph, with the overall shown below the graph.

NOTE: Hitting `traing model` button before runnning through the project to complete in `Parallel` will have no effect, due to the fact that the final model will have yet to be generated. 

