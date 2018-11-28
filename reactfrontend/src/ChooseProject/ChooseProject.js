import React, { Component } from 'react';
import { Link } from 'react-router-dom';

export class ChooseProject extends Component {
  constructor(props) {
    super(props);

    this.state = {
      dest: this.props.match.params.dest,
      projects: [],
      project: ''
    };

    this.onChange = this.onChange.bind(this);
  }

  async componentWillMount() {
    const res = await fetch(`/${this.state.dest}/list_models`);
    const projects = await res.json();

    this.setState({ projects, project: projects[0] });
  }

  onChange(event) {
    this.setState({ project: event.target.value });
  }

  render() {
    const { projects, project } = this.state;

    const projectSelect =
      projects.length > 0 ? (
        <div className="row">
          <select
            className="two-thirds column"
            name="project"
            id="project"
            value={project}
            onChange={this.onChange}
          >
            {projects.map(project => (
              <option value={project} key={project}>
                {project}
              </option>
            ))}
          </select>
          <Link
            to={`/${this.state.dest}/${project}`}
            className="button button-primary one-third column"
          >
            Submit
          </Link>
        </div>
      ) : (
        <p>No Projects</p>
      );
    return (
      <div>
        <br />
        <div className="section hero">
          <div className="container">
            <h3 className="section-heading">
              {this.state.dest} | Choose Project
            </h3>
            {projectSelect}
          </div>
        </div>
      </div>
    );
  }
}

export default ChooseProject;
