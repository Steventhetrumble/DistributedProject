import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import * as tf from '@tensorflow/tfjs'

class App extends Component {
  constructor(){
    super();
    this.state={
      model:{},
      X:[],
      Y:[],
    }
  }

  async componentDidMount(){
    try{
      const tempmodel = await tf.loadModel(tf.io.browserHTTPRequest('http://127.0.0.1:5000/myview/method1/model'))
      console.log(tempmodel)
      this.setState({model:tempmodel })
      const res = await fetch('http://127.0.0.1:5000/myview/method2/')
      const tempData = await res.json();
      console.log(tempData);



    }catch(e){
      console.log(e);
    }
  }


  render() {
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <p>
            Edit <code>src/App.js</code> and save to reload.
          </p>
          <a
            className="App-link"
            href="https://reactjs.org"
            target="_blank"
            rel="noopener noreferrer"
          >
            Learn React
          </a>
        </header>
      </div>
    );
  }
}

export default App;
