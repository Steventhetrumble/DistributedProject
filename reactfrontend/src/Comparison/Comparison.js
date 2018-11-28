import React, { Component } from 'react';
//import logo from './logo.svg';
import './Comparison.css';
import * as tf from '@tensorflow/tfjs';
import LossChart from '../LossChart/LossChart';

class Comparison extends Component {
  constructor() {
    super();
    this.state = {
      model: {},
      X: [],
      Y: [],
      epochs: 5,
      learningRate: 0.05,
      lossArray: []
    };
  }

  async componentDidMount() {
    try {
      const tempmodel = await tf.loadModel(
        tf.io.browserHTTPRequest('/myview/method1/model')
      );
      this.setState({ model: tempmodel });

      const res = await fetch('/myview/method2/');
      var tempX = [];
      var tempY = [];

      await res.json().then(element => {
        element.forEach(element => {
          var i;
          var littlex = [];

          for (i = 0; i < element.length; i++) {
            //The seventh index is the scaled estimated cost in this model-- the label
            if (i === 8) {
              tempY.push(element[i]);
            } else littlex.push(element[i]);
          }
          tempX.push(littlex);
        });
      });

      this.setState({
        X: tempX,
        Y: tempY
      });
    } catch (e) {
      console.log(e);
    }
  }
  async trainModel() {
    // console.log(this.state.Y);
    const xs = tf.tensor2d(this.state.X);
    const ys = tf.tensor1d(this.state.Y);
    this.state.model.compile({ optimizer: 'adam', loss: 'meanSquaredError' });
    var tempArray = [];
    const h = await this.state.model.fit(xs, ys, {
      batchSize: 5,
      epochs: this.state.epochs,
      callbacks: {
        onEpochEnd: async (epoch, log) => {
          console.log(`Epoch ${epoch}: loss = ${log.loss}`);
          tempArray.push([epoch, log.loss]);
        }
      }
    });
    console.log(h.history.loss);
    const resultOfSave = await this.state.model.save(
      tf.io.browserHTTPRequest('/myview/method3/')
    );
    await this.setState({ lossArray: tempArray });
    console.log(resultOfSave);
    // console.log("Loss after Epoch:" + h.history.loss[0]);

    // this.setState({lossArray:h.history.loss})
  }

  render() {
    let lossArray = this.state.lossArray.length
      ? this.state.lossArray
      : [[0, 0]];
    return (
      <div className="Comparison">
        <br />
        <div className="section hero">
          <div className="container">
            <h3 className="section-heading">Need help getting started?</h3>
            <p className="section-description">
              To get started, click on the Train Model Button!
            </p>
            <div className="sixteen columns">
              <div className="ten columns offset-by-one">
                <LossChart
                  lossArray={lossArray}
                  epochs={this.state.epochs - 1}
                />
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

export default Comparison;
