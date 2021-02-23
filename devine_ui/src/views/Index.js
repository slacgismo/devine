import React from "react";
// node.js library that concatenates classes (strings)
import classnames from "classnames";
// javascipt plugin for creating charts
// import Chart from "chart.js";
// react plugin used to create charts
import { Line, Bar } from "react-chartjs-2";
import Chart from 'react-apexcharts'

// reactstrap components
import {
  Button,
  Card,
  CardHeader,
  CardBody,
  NavItem,
  NavLink,
  Nav,
  Progress,
  Table,
  Container,
  Row,
  Col
} from "reactstrap";

// core components
import {
  chartOptions,
  parseOptions,
  chartExample1,
  chartExample2
} from "variables/charts.js";

import Header from "components/Headers/Header.js";


class Index extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      activeNav: 1,
      uniqueDriversSeries: [{
        name: 'Unique Drivers',
        data: [4, 5, 7, 16, 14, 10, 2]
      }],
      sessionsSeries: [{
        name: 'Sessions',
        data: [3, 6, 8, 15, 13, 18, 4]
      }],
      stationStatusSeries: [{
        name: '  In Use',
        data: [44]
      }, {
        name: '  Available',
        data: [76]
      }, {
        name: '  Not Ready',
        data: [35]
      }, {
        name: '  Watch List',
        data: [5]
      }, {
        name: '  Needs Servicce',
        data: [12]
      }],
      avgSessionLenSeries: [{
        name: 'Charging',
        data: [90, 55]
      }, {
        name: 'Idle',
        data: [10, 32]
      }],
      avgSessionLenOptions: {
        chart: {
          type: 'bar',
          height: 350,
          stacked: true,
          stackType: '100%'
        },
        plotOptions: {
          bar: {
            horizontal: true,
          },
        },
        stroke: {
          width: 1,
          colors: ['#fff']
        },
        xaxis: {
          categories: ["Weekdays", "Weekends"],
        },
        tooltip: {
          y: {
            formatter: function (val) {
              return val + "K"
            }
          }
        },
        fill: {
          opacity: 1
        
        },
        legend: {
          position: 'top',
          horizontalAlign: 'left',
          offsetX: 40
        }
      },
      stationStatusOptions: {
        chart: {
          type: 'bar',
          height: 350
        },
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: '55%',
          },
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          show: true,
          width: 2,
          colors: ['transparent']
        },
        xaxis: {
          categories: ['', '', '', '', ''],
        },
        colors: ['#3498DB', '#28B463', '#808B96', '#F4D03F', '#E74C3C'],
        yaxis: {
          title: {
            text: 'Number of Parts'
          }
        },
        fill: {
          opacity: 1
        },
        tooltip: {
          y: {
            formatter: function (val) {
              return "$ " + val + " thousands"
            }
          }
        },
        legend: {
          position: "right",
          fontSize: '16px',
          markers: {
            width: 24,
            height: 24,
          }
        }
      },
      uniqueDriversOptions: {
        chart: {
          type: 'bar',
          height: 350
        },
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: '55%',
          },
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          show: true,
          width: 2,
          colors: ['transparent']
        },
        xaxis: {
          categories: ['11/18', '11/19', '11/20', '11/21', '11/22', '11/23', '11/24',],
        },
        yaxis: {
          title: {
          }
        },
        fill: {
          opacity: 1
        },
        tooltip: {
          y: {
            formatter: function (val) {
              return "$ " + val + " thousands"
            }
          }
        }
      },
      sessionsOptions: {
        chart: {
          type: 'bar',
          height: 350
        },
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: '55%',
          },
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          show: true,
          width: 2,
          colors: ['transparent']
        },
        colors: ['#F39C12'],
        xaxis: {
          categories: ['11/18', '11/19', '11/20', '11/21', '11/22', '11/23', '11/24',],
        },
        yaxis: {
          title: {
          }
        },
        fill: {
          opacity: 1
        },
        tooltip: {
          y: {
            formatter: function (val) {
              return "$ " + val + " thousands"
            }
          }
        }
      },
    };
    if (window.Chart) {
      // parseOptions(Chart, chartOptions());
    }
  }
  toggleNavs = (e, index) => {
    e.preventDefault();
    this.setState({
      activeNav: index,
      // chartExample1Data:
      //   this.state.chartExample1Data === "data1" ? "data2" : "data1"
    });
  };
  render() {
    return (
      <>
        <Header/>
        {/* Page content */}
        <Container className="mt--7" fluid>
          <Row>
            <Col className="mb-5 mb-xl-0" xl="8">
              <Card className="shadow">
                <CardHeader className="bg-transparent">
                  <Row className="align-items-center">
                    <div className="col">
                      <h3 className="mb-0">Station Status</h3>
                    </div>
                  </Row>
                </CardHeader>
                <CardBody>
                  {/* Chart */}
                  <Chart options={this.state.stationStatusOptions} series={this.state.stationStatusSeries} type="bar" width={1050} height={500} />

                </CardBody>
              </Card>
            </Col>
            <Col xl="4">
              <Row>
              <Card className="shadow">
                <CardHeader className="bg-transparent">
                  <Row className="align-items-center">
                    <div className="col">
                      <h3 className="mb-0">Unique Drivers</h3>
                    </div>
                  </Row>
                </CardHeader>
                <CardBody>
                  {/* Chart */}
                  <Chart options={this.state.sessionsOptions} series={this.state.uniqueDriversSeries} type="bar" width={500} height={176} />
                </CardBody>
              </Card>
              
              </Row>
              {/* Adjust space between rows, mt-x*/}
              <Row className="mt-3">
              <Card className="shadow">
                <CardHeader className="bg-transparent">
                  <Row className="align-items-center">
                    <div className="col">
                      <h3 className="mb-0">Sessions</h3>
                    </div>
                  </Row>
                </CardHeader>
                <CardBody>
                  {/* Chart */}
                  <Chart options={this.state.uniqueDriversOptions} series={this.state.sessionsSeries} type="bar" width={500} height={176} />
                </CardBody>
              </Card>
              </Row>
              
            </Col>
          </Row>
          <Row className="mt-3">
            <Col className="mb-5 mb-xl-0" xl="8">
              <Card className="shadow">
                <CardHeader className="border-0">
                  <Row className="align-items-center">
                    <div className="col">
                      <h3 className="mb-0">Environment</h3>
                    </div>
                  </Row>
                </CardHeader>
                <CardBody>
                  <img
                    alt="..."
                    src={require("assets/img/theme/environment.png")}
                  />
                </CardBody>
                
              </Card>
            </Col>
            <Col xl="4">
              <Row>
              <Card className="shadow">
                <CardHeader className="bg-transparent">
                  <Row className="align-items-center">
                    <div className="col">
                      <h3 className="mb-0">Unique Drivers</h3>
                    </div>
                  </Row>
                </CardHeader>
                <CardBody>
                  {/* Chart */}
                  <Chart options={this.state.avgSessionLenOptions} series={this.state.avgSessionLenSeries} type="bar" width={500} height={190} />
                </CardBody>
              </Card>
              </Row>
              
            </Col>
          </Row>
        </Container>
      </>
    );
  }
}

export default Index;
