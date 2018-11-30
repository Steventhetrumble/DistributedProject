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
