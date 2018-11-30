import React, { Component } from 'react';
import './Sequential.css';
import * as tf from '@tensorflow/tfjs';
import classNames from 'classnames';
import ApexLossChart from '../ApexLossChart/ApexLossChart';
import { Link } from 'react-router-dom';

class Sequential extends Component {
  constructor() {
    super();
    this.state = {
      training: false,
      complete: false,
      model: {},
      X: [],
      Y: [],
      epochs: [1, 5, 10, 15, 20],
      epochsCount: 20,
      learningRate: 0.1,
      lossArray: []
    };

    this.onChange = this.onChange.bind(this);
  }

  async componentDidMount() {
    try {
      const tempmodel = await tf.loadModel(
        tf.io.browserHTTPRequest('/Sequential/get_model/model')
      );
      this.setState({ model: tempmodel });

      const res = await fetch('/Sequential/get_train_data');
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
    this.setState({ training: true, lossArray: [] });
    // console.log(this.state.Y);
    // const tempArray = [];

    const xs = tf.tensor2d(this.state.X);
    const ys = tf.tensor1d(this.state.Y);
    this.state.model.compile({ optimizer: 'adam', loss: 'meanSquaredError' });

    await this.state.model.fit(xs, ys, {
      batchSize: 5,
      epochs: this.state.epochsCount,
      callbacks: {
        onEpochEnd: async (epoch, log) => {
          console.log(`Epoch ${epoch}: loss = ${log.loss}`);
          // tempArray.push(log.loss);
          this.setState({ lossArray: [...this.state.lossArray, log.loss] });
        }
      }
    });

    xs.dispose();
    ys.dispose();

    await this.state.model.save(
      tf.io.browserHTTPRequest('/Sequential/put_final_model')
    );
    // console.log("Loss after Epoch:" + h.history.loss[0]);

    // this.setState({lossArray:h.history.loss})
    this.setState({ training: false, complete: true });
  }

  onChange(event) {
    this.setState({ epochsCount: event.target.value });
  }

  render() {
    const { lossArray, epochs, epochsCount, training, complete } = this.state;

    return (
      <div className="Sequential">
        <br />
        <div className="section hero">
          <div className="container">
            <h3 className="section-heading">Sequential</h3>
            <p className="section-description">
              To get started, click on the Train Model Button!
            </p>
            <div className="sixteen columns">
              <div className="ten columns offset-by-one">
                {/* <LossChart lossArray={lossArray} epochs={epochsCount - 1} /> */}
                <ApexLossChart series={lossArray} />
                <br />
                {lossArray.length > 0 ? (
                  <h5>
                    Current Loss:{' '}
                    {parseFloat(lossArray[lossArray.length - 1]).toFixed(9)}
                  </h5>
                ) : (
                  ''
                )}
                <div className="row">
                  <select
                    name="epochs"
                    id="epochs"
                    className="two columns"
                    value={epochsCount}
                    onChange={this.onChange}
                  >
                    {epochs.map(epoch => (
                      <option value={epoch} key={epoch}>
                        {epoch}
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
                    onClick={() => this.trainModel()}
                    disabled={training}
                  >
                    {!complete
                      ? training
                        ? 'Training...'
                        : 'Start Training Model'
                      : 'Training Complete'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default Sequential;
