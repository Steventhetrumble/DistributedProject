import React, { Component } from 'react';
//import logo from './logo.svg';
import './Team.css';

class Team extends Component {
  render() {
    return (
      <div className="App">
        <div className="section hero">
          <div className="container">
            <div className="sixteen columns">
              <div className="ten columns offset-by-one">
                <br />
                <table className="u-full-width">
                  <thead>
                    <tr>
                      <th>Group Members</th>
                      <th>GitHub</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Nate Aldred</td>
                      <td>
                        <a href="http://github.com/Nate60">GitHub</a>
                      </td>
                    </tr>
                    <tr>
                      <td>Luke Baal</td>
                      <td>
                        <a href="http://github.com/LukeBaal">GitHub</a>
                      </td>
                    </tr>
                    <tr>
                      <td>Graeham Broda</td>
                      <td>
                        <a href="http://github.com/graeham13">GitHub</a>
                      </td>
                    </tr>
                    <tr>
                      <td>Steven Trumble</td>
                      <td>
                        <a href="http://github.com/steventhetrumble">GitHub</a>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default Team;
