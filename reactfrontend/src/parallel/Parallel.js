import React, { Component } from 'react';
//import logo from './logo.svg';
import './Parallel.css';
import * as tf from '@tensorflow/tfjs';
import LossChart from '../LossChart/LossChart';



function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
class Parallel extends Component {
  constructor(){
    super();
    this.state={
      model:{},
      X:[],
      Y:[],
      epochs:1,
      learningRate: 0.1,
      lossArray:[]
    }
  }
  
  async trainModel(){
    try{
      var task = await fetch('http://127.0.0.1:8080/Parallel/check_model_for_down/Test_Project')
      var path;
      await task.json().then(element =>{
        path = element.result
      })
      
      console.log(path)
      if(path === 'wait'){
        console.log('wait')
        return
      }
      if(path === 'done'){
        console.log(" is complete")
        return
      }
      console.log(path)
      const tempModelPath = 'http://127.0.0.1:8080/Parallel/get_Model/Test_Project/'+ path +'/model'
      const tempmodel = await tf.loadModel(tf.io.browserHTTPRequest(tempModelPath))
      this.setState({model:tempmodel })
      const dataPath = 'http://127.0.0.1:8080/Parallel/get_data/Test_Project/' + path
      const res = await fetch(dataPath)
      var tempX = [];
      var tempY = [];
      
      await res.json().then(element => {
       element.forEach(element => {
        var i;
        var littlex=[];
        
        for(i = 0 ; i < element.length ; i ++){
          //The seventh index is the scaled estimated cost in this model-- the label
          if(i === 8){
            tempY.push(element[i])
          }
          else littlex.push(element[i])
        }
        tempX.push(littlex);
       });        
      });
      
      this.setState({
        X:tempX,
        Y:tempY,
      })
      const xs = tf.tensor2d(this.state.X);
    const ys = tf.tensor1d(this.state.Y);
    this.state.model.compile({optimizer: 'adam', loss: 'meanSquaredError'});
    var tempArray = [];
    const h = await this.state.model.fit(xs,ys,{
      batchSize: 5,
      epochs: this.state.epochs,
      callbacks: {
        onEpochEnd: async (epoch, log) => {
          console.log(`Epoch ${epoch }: loss = ${log.loss}`);
          tempArray.push([epoch ,log.loss]);
        }
      }
    });
    console.log(h.history.loss);
    const resultPath = 'http://127.0.0.1:8080/Parallel/put_model/Test_Project/' +path 
    const resultOfSave = await this.state.model.save(tf.io.browserHTTPRequest(resultPath));
    await this.setState({lossArray:tempArray});
    console.log(resultOfSave)

    }catch(e){
      console.log(e);
    }


    // console.log(this.state.Y);
    
    // console.log("Loss after Epoch:" + h.history.loss[0]);
    
    // this.setState({lossArray:h.history.loss})

  }


  render() {
    let lossArray = this.state.lossArray.length ? this.state.lossArray : [[0,0]];
    return (
      <div className="Parallel">
        <br/>
        <div className="section hero">
          <div className="container">
            <h3 className="section-heading">Need help getting started?</h3>
            <p className="section-description">To get started, click on the Train Model Button!</p>
            <div className="sixteen columns">
              <div className="ten columns offset-by-one">
                <LossChart lossArray={lossArray} epochs={this.state.epochs - 1} />
                <br/>
                {/* eslint-disable-next-line */}
                <a className="button button-primary" onClick={() => this.trainModel()}>Start Training Model</a>
              </div>
            </div>
            
          </div>
        </div>
      </div>
    );
  }
}

export default Parallel;
