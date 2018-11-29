import React, { Component } from 'react';
import Chart from 'react-apexcharts';

export class ApexLossChart extends Component {
  constructor(props) {
    super(props);

    this.state = {
      options: {
        title: {
          text: 'Epoch vs. Loss',
          align: 'center'
        },
        chart: {
          id: 'loss-chart'
        },
        xaxis: {
          type: 'numeric',
          labels: {
            hideOverlappingLabels: true
          }
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          width: 3
        },
        markers: {
          size: 0,
          hover: {
            size: 7
          }
        },
        tooltip: {
          y: {
            formatter: val => val.toExponential(3)
          }
        }
      }
    };
  }

  render() {
    return (
      <Chart
        options={this.state.options}
        series={[
          {
            name: 'Loss',
            data: this.props.series
          }
        ]}
        type="line"
        width={600}
        height={400}
      />
    );
  }
}

export default ApexLossChart;
