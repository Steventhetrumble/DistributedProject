import React, { Component } from 'react';
import * as tf from '@tensorflow/tfjs';
import LossChart from '../LossChart/LossChart';
import classNames from 'classnames';

class Comparison extends Component {
  constructor() {
    super();
    this.state = {
      training: false,
      complete: false,
      model: {},
      X: [],
      Y: [],
      seq_results: [],
      seq_result: null
    };

    this.onChange = this.onChange.bind(this);
  }

  async componentDidMount() {
    try {
      const tempmodel = await tf.loadModel(
        tf.io.browserHTTPRequest('/Parallel/get_final_model/Test_Project/model')
      );
      this.setState({ model: tempmodel });
      const res = await fetch('/Parallel/get_test_data/Test_Project');
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
    this.setState({ training: true });
    let predictions;
    await tf.tidy(() => {
      console.log(this.state.X);
      const xs = tf.tensor2d(this.state.X);
      predictions = this.state.model.predict(xs).dataSync();
    });

    const results = [];
    let result;
    await tf.tidy(() => {
      result = tf.losses.meanSquaredError(this.state.Y, predictions).dataSync();
      predictions.forEach((prediction, index) => {
        results.push([
          index,
          tf.losses.meanSquaredError(this.state.Y[index], prediction).dataSync()
        ]);
      });
    });

    this.setState({
      seq_results: results,
      seq_result: result,
      training: false,
      complete: true
    });
  }

  onChange(event) {
    this.setState({ epochsCount: event.target.value });
  }

  render() {
    const { seq_results, seq_result, testing, complete } = this.state;

    return (
      <div>
        <br />
        <div className="section hero">
          <div className="container">
            <h3 className="section-heading">Comparison</h3>
            <p className="section-description">
              To get started, click on the Train Model Button!
            </p>
            <div className="sixteen columns">
              <div className="ten columns offset-by-one">
                <LossChart lossArray={seq_results} epochs={20} />
                <br />
                {seq_results.length > 0 ? (
                  <h5>
                    Mean Squared Error: {parseFloat(seq_result).toFixed(9)}
                  </h5>
                ) : (
                  ''
                )}
                <button
                  className={classNames({
                    button: !testing,
                    'button-primary': !testing && !complete
                  })}
                  style={{ cursor: testing ? 'progress' : 'pointer' }}
                  onClick={() => this.trainModel()}
                  disabled={testing | complete}
                >
                  {!complete
                    ? testing
                      ? 'Testing...'
                      : 'Start testing Model'
                    : 'Testing Complete'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default Comparison;
