import React, { Component } from 'react';
import './Parallel.css';
import * as tf from '@tensorflow/tfjs';
import classNames from 'classnames';
import ApexLossChart from '../ApexLossChart/ApexLossChart';
import { Link } from 'react-router-dom';

// function sleep(ms) {
//   return new Promise(resolve => setTimeout(resolve, ms));
// }

class Parallel extends Component {
  constructor(props) {
    super(props);

    this.state = {
      complete: false,
      training: false,
      project: this.props.match.params.project,
      path: '',
      task: null,
      iteration: null,
      progress: 0,
      model: {},
      X: [],
      Y: [],
      epoch: 0,
      learningRate: 0.1,
      iterationCount: 1,
      iterations: [1, 5, 10, 15],
      flatData: []
    };

    this.onIterationsChange = this.onIterationsChange.bind(this);
  }

  async componentWillMount() {
    await this.getLossResults();
    await this.getProgress();
  }

  async getLossResults() {
    const res = await fetch(`/Parallel/get_loss/${this.state.project}`);

    const data = await res.json();
    const flatData = await data.map(entry => entry[0]);

    this.setState({ flatData });
  }

  async trainModelMultiple() {
    this.setState({ training: true });

    for (let i = 0; i < this.state.iterationCount; i++) {
      await this.trainModel();
    }
    this.setState({ training: false });
  }

  async trainModel() {
    try {
      const status = await fetch(
        `/Parallel/check_model_for_down/${this.state.project}`
      );
      let path;
      await status.json().then(element => {
        path = element.result;
      });

      console.log(path);
      if (path === 'wait') {
        setTimeout(this.trainModel(), 1000);
        return;
      }
      if (path === 'done') {
        console.log(' is complete');
        this.setState({ path: 'complete', complete: true, training: false });
        return;
      }
      const tempModelPath = `/Parallel/get_Model/${
        this.state.project
      }/${path}/model`;
      const tempmodel = await tf.loadModel(
        tf.io.browserHTTPRequest(tempModelPath)
      );
      this.setState({ model: tempmodel });
      const dataPath = `/Parallel/get_data/${this.state.project}/${path}`;
      const res = await fetch(dataPath);
      let tempX = [];
      let tempY = [];

      const labelIndexRes = await fetch(
        `/Parallel/get_label_index/${this.state.project}`
      );
      const labelIndex = await labelIndexRes.json();

      await res.json().then(element => {
        element.forEach(element => {
          let i;
          let littlex = [];

          for (i = 0; i < element.length; i++) {
            //The seventh index is the scaled estimated cost in this model-- the label
            if (i === labelIndex[0]) {
              tempY.push(element[i]);
            } else littlex.push(element[i]);
          }
          tempX.push(littlex);
        });
      });

      const iteration = /^[0-9]+/.exec(path)[0];
      const task = /[0-9]+$/.exec(path)[0];

      this.setState({
        path,
        task,
        iteration,
        X: tempX,
        Y: tempY
      });

      const xs = tf.tensor2d(this.state.X);
      const ys = tf.tensor1d(this.state.Y);
      this.state.model.compile({
        optimizer: 'adam',
        loss: 'meanSquaredError'
      });
      let tempArray = [];
      await this.state.model.fit(xs, ys, {
        batchSize: 5,
        epochs: 1,
        callbacks: {
          onEpochEnd: async (epoch, log) => {
            console.log(`Epoch ${epoch}: loss = ${log.loss}`);
            tempArray = [this.state.epoch, log.loss];
            this.setState({ epoch: this.state.epoch + 1 });
          }
        }
      });
      const resultPath = `/Parallel/put_model/${this.state.project}/${path}/${
        tempArray[1]
      }`;
      await this.state.model.save(tf.io.browserHTTPRequest(resultPath));

      await this.getLossResults();
      await this.getProgress();
    } catch (e) {
      console.log(e);
    }
  }

  getProgress() {
    const progress =
      ((parseInt(this.state.iteration) +
        1 +
        (parseInt(this.state.task) + 1) / 5) /
        20) *
      100;

    this.setState({ progress: progress ? Math.floor(progress) : 0 });
  }

  onIterationsChange(event) {
    this.setState({ iterationCount: event.target.value });
  }

  render() {
    const {
      project,
      complete,
      training,
      task,
      iteration,
      progress,
      iterations,
      flatData
    } = this.state;

    const header =
      progress !== 0 ? (
        <p className="section-description">
          Iteration: {iteration} | task: {task} | Progress: {progress}%
        </p>
      ) : (
        <p className="section-description">
          To get started, click on the Train Model Button!
        </p>
      );
    return (
      <div className="Parallel">
        <br />
        <div className="section hero">
          <div className="container">
            <h3 className="section-heading">Parallel</h3>
            {header}
            {/* <LossChart lossArray={lossArray} epochs={epochs - 1} /> */}
            {flatData.length > 0 ? (
              <React.Fragment>
                <ApexLossChart series={flatData} />
                <h5>
                  Current Loss:{' '}
                  {parseFloat(flatData[flatData.length - 1]).toFixed(9)}
                </h5>
              </React.Fragment>
            ) : (
              ''
            )}

            <div className="row">
              <select
                className="two columns"
                name="iterations"
                id="iterations"
                value={this.state.iterationCount}
                onChange={this.onIterationsChange}
              >
                {iterations.map(iter => (
                  <option value={iter} key={iter}>
                    {iter}
                  </option>
                ))}
              </select>
              <button
                className={classNames({
                  button: !training,
                  eight: true,
                  columns: true,
                  'button-primary': !training
                })}
                style={{ cursor: training ? 'progress' : 'pointer' }}
                onClick={() => this.trainModelMultiple()}
                disabled={training}
              >
                {!complete
                  ? training
                    ? 'Training...'
                    : 'Start Training Model'
                  : 'Training Complete'}
              </button>
            </div>
            <Link
              to={`/Evaluation/${project}`}
              className="button button-primary"
            >
              Evaluate
            </Link>
          </div>
        </div>
      </div>
    );
  }
}

export default Parallel;
