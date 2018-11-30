# Backend

## Install

```
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

Setup admin account and database

```
fabmanager create-db
fabmanager create-admin
```

Follow the prompts to create the admin account (Remember username and password)

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

   - Project Name: TestProject
   - Steps per Iteration: 1000
   - Max Steps: 20000
   - Data Size: 1000
   - Data Split Size: 200
   - Label Index: 8

1. Click Save
1. Terminate the server and run it again
1. Click the checkbox beside the new model entry
1. Click the action dropdown and select 'Create Project Directory'
1. For the Model, click upload and upload 'trained_model.h5' located in SampleData&Model in the flaskbackend directory.
   - NOTE: the h5 file is a saved Keras model, defining model structure and possible starting weights
1. Click submit
1. For the Training data, click upload and upload 'training_data.csv' located in SampleData&Model in the flaskbackend directory.
1. Click submit
1. For the Testing data, click upload and upload 'testing_data.csv' located in SampleData&Model in the flaskbackend directory.
1. Click submit
1. Wait for 'complete' to appear on the screen.

Backend is now ready to serve tasks to the client
