import React, { Component } from 'react';
import { Route } from 'react-router-dom';
import './App.css';
import Sequential from './Sequential/Sequential';
import Parallel from './parallel/Parallel';
import Evaluation from './Evaluation/Evaluation';
import Team from './Team/Team';
import ChooseProject from './ChooseProject/ChooseProject';
import { Link } from 'react-router-dom';

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
          <Link to="/">Home</Link>
          <Link to="/Sequential">Sequential</Link>
          <Link to="/Parallel">Parallel</Link>
          {/* <Link to="/Evaluation">Evaluation</Link> */}
          <Link to="/Team">Team</Link>
          <button className="icon" onClick={() => this.openDrawerMenu()}>
            &#9776;
          </button>
        </div>
        <div className="section hero">
          <div className="container">
            <div className="sixteen columns">
              <div className="ten columns offset-by-one">
                {/* <Route exact path="/Home" component={Home} /> */}
                <Route exact path="/" component={ChooseProject} />
                <Route exact path="/Sequential" component={Sequential} />
                <Route exact path="/Parallel" component={ChooseProject} />
                <Route exact path="/Parallel/:project" component={Parallel} />
                <Route
                  exact
                  path="/Evaluation/:project"
                  component={Evaluation}
                />
                <Route exact path="/Team" component={Team} />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default App;
