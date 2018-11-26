import React, { Component } from 'react';
import './Parallel.css';
import * as tf from '@tensorflow/tfjs';
import LossChart from '../LossChart/LossChart';
import { profile } from '@tensorflow/tfjs';

// function sleep(ms) {
//   return new Promise(resolve => setTimeout(resolve, ms));
// }
class Parallel extends Component {
  constructor() {
    super();
    this.state = {
      path: '',
      task: null,
      iteration: null,
      progress: 0,
      model: {},
      X: [],
      Y: [],
      epochs: 1,
      epoch: 0,
      learningRate: 0.1,
      lossArray: [[0, 0]]
    };
  }

  componentWillMount() {
    this.getLossResults();
    this.getProgress();
  }

  async getLossResults() {
    const res = await fetch(
      'http://127.0.0.1:8080/Parallel/get_loss/Test_Project'
    );

    const data = await res.json();
    console.log(data);
    this.setState({ lossArray: data });
  }

  async trainModel() {
    try {
      const status = await fetch(
        'http://127.0.0.1:8080/Parallel/check_model_for_down/Test_Project'
      );
      let path;
      await status.json().then(element => {
        path = element.result;
      });

      console.log(path);
      if (path === 'wait') {
        console.log('wait');

        setTimeout(() => this.trainModel(), 1000);
      }
      if (path === 'done') {
        console.log(' is complete');
        return;
      }
      console.log(path);
      const tempModelPath =
        'http://127.0.0.1:8080/Parallel/get_Model/Test_Project/' +
        path +
        '/model';
      const tempmodel = await tf.loadModel(
        tf.io.browserHTTPRequest(tempModelPath)
      );
      this.setState({ model: tempmodel });
      const dataPath =
        'http://127.0.0.1:8080/Parallel/get_data/Test_Project/' + path;
      const res = await fetch(dataPath);
      let tempX = [];
      let tempY = [];

      await res.json().then(element => {
        element.forEach(element => {
          let i;
          let littlex = [];

          for (i = 0; i < element.length; i++) {
            //The seventh index is the scaled estimated cost in this model-- the label
            if (i === 8) {
              tempY.push(element[i]);
            } else littlex.push(element[i]);
          }
          tempX.push(littlex);
        });
      });

      const task = /^[0-9]+/.exec(path)[0];
      const iteration = /[0-9]+$/.exec(path)[0];

      this.setState({
        path,
        task,
        iteration,
        X: tempX,
        Y: tempY
      });

      const xs = tf.tensor2d(this.state.X);
      const ys = tf.tensor1d(this.state.Y);
      this.state.model.compile({ optimizer: 'adam', loss: 'meanSquaredError' });
      let tempArray = [];
      const h = await this.state.model.fit(xs, ys, {
        batchSize: 5,
        epochs: this.state.epochs,
        callbacks: {
          onEpochEnd: async (epoch, log) => {
            console.log(`Epoch ${epoch}: loss = ${log.loss}`);
            tempArray = [this.state.epoch, log.loss];
            this.setState({ epoch: this.state.epoch + 1 });
          }
        }
      });
      console.log(h.history.loss);
      const resultPath = `http://127.0.0.1:8080/Parallel/put_model/Test_Project/${path}/${
        tempArray[1]
      }`;
      const resultOfSave = await this.state.model.save(
        tf.io.browserHTTPRequest(resultPath)
      );
      // await this.setState({
      //   lossArray: this.state.lossArray.concat(tempArray)
      // });
      // await this.state.lossArray.push(tempArray);

      await this.getLossResults();
      await this.getProgress();
      console.log(resultOfSave);
    } catch (e) {
      console.log(e);
    }

    // console.log(this.state.Y);

    // console.log("Loss after Epoch:" + h.history.loss[0]);

    // this.setState({lossArray:h.history.loss})
  }

  getProgress() {
    const progress =
      ((parseInt(this.state.task) +
        1 +
        (parseInt(this.state.iteration) + 1) / 5) /
        20) *
      100;

    this.setState({ progress: progress ? Math.floor(progress) : 0 });
  }

  render() {
    const { lossArray, epochs, task, iteration, progress } = this.state;

    const header =
      progress !== 0 ? (
        <p className="section-description">
          Task: {task} | iteration: {iteration} | Progress: {progress}%
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
            <h3 className="section-heading">Need help getting started?</h3>
            {header}
            <div className="sixteen columns">
              <div className="ten columns offset-by-one">
                <LossChart lossArray={lossArray} epochs={epochs - 1} />
                <br />
                {/* eslint-disable-next-line */}
                <a
                  className="button button-primary"
                  onClick={() => this.trainModel()}
                >
                  Start Training Model
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default Parallel;
