import React, { Component } from 'react';
//import logo from './logo.svg';
import './Home.css';
import { Link } from 'react-router-dom';

class Home extends Component {
  render() {
    return (
      <div className="App">
        <div className="section hero">
          <div className="container">
            <br />
            <div className="row">
              <Link
                to="/Sequential"
                className="button button-primary one-half column"
              >
                Sequential
              </Link>
              <Link
                to="/Choose/Parallel"
                className="button button-primary one-half column"
              >
                Parallel
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default Home;
