import React, { Component } from 'react';
import { Route } from 'react-router-dom';
//import logo from './logo.svg';
import './App.css';
import Sequential from './Sequential/Sequential';
import Parallel from './parallel/Parallel';
import Home from './Home/Home';
import Comparison from './Comparison/Comparison';
import Team from './Team/Team';

class App extends Component {
  async openDrawerMenu() {
    var x = document.getElementById('mainNavBar');
    if (x.className === 'navBar') {
      x.className += ' responsive';
    } else {
      x.className = 'navBar';
    }
  }

  render() {
    return (
      <div className="App">
        <div className="navBar" id="mainNavBar">
          <a href="/Home">Home</a>
          <a href="/Sequential">Sequential</a>
          <a href="/Parallel">Parallel</a>
          <a href="/Comparison">Comparison</a>
          <a href="/Team">Team</a>
          <button className="icon" onClick={() => this.openDrawerMenu()}>
            &#9776;
          </button>
        </div>
        <div className="section hero">
          <div className="container">
            <div className="sixteen columns">
              <div className="ten columns offset-by-one">
                <Route path="/Home" component={Home} />
                <Route path="/Sequential" component={Sequential} />
                <Route path="/Parallel" component={Parallel} />
                <Route path="/Comparison" component={Comparison} />
                <Route path="/Team" component={Team} />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default App;
