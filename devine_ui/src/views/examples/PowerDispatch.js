import React from "react";
import Chart from 'react-apexcharts'
import Switch from "react-switch";
// reactstrap components
import {
  Button,
  Card,
  CardHeader,
  CardBody,
  FormGroup,
  Form,
  Input,
  Container,
  Row,
  Col
} from "reactstrap";
// core components
import Header from "components/Headers/Header.js";

class PowerDispatch extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
    
      systemLoadSeries: [{
        name: "kW",
        data: [25, 35, 70, 80, 90, 95, 85, 80, 75, 70, 55, 80, 120, 140, 180, 185, 180, 160, 140, 130, 115, 90, 70, 30]
      }],
      
      systemLoadOptions: {
        chart: {
          height: 350,
          type: 'line',
          zoom: {
            enabled: false
          }
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          curve: 'straight'
        },
        xaxis: {
          title: {
            text: 'Hours'
          }
        },
        yaxis: {
          title: {
            text: 'System Load (kW)'
          }
        },
        annotations: {
          xaxis: [{
            x: 24,
            strokeDashArray: 10,
            borderColor: '#ABB2B9',
            label: {
              borderColor: '#ABB2B9',
              style: {
                color: '#fff',
                background: '#ABB2B9',
              },
              text: 'End of Day',
            }
          }],
          yaxis: [{
            y: 180,
            strokeDashArray: 10,
            borderColor: '#E74C3C',
            label: {
              borderColor: '#E74C3C',
              style: {
                color: '#fff',
                background: '#E74C3C',
              },
              text: 'System Capacity',
            }
          }]
        },
        grid: {
          row: {
            colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
            opacity: 0.5
          },
        },
        xaxis: {
          categories: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, ],
        }
      },
    
      resourcesSeries: [{
        name: '  Available',
        data: [44, 55, 41]
      }, {
        name: '  Utilized',
        data: [13, 23, 20]
      }],
      resourcesOptions: {
        chart: {
          type: 'bar',
          height: 350,
          stacked: true,
          stackType: '100%'
        },
        responsive: [{
          breakpoint: 480,
          options: {
            legend: {
              position: 'bottom',
              offsetX: -10,
              offsetY: 0
            }
          }
        }],
        colors: ['#28B463', '#F4D03F'],

        xaxis: {
          categories: ['PV', 'Batteries', 'Chargers'],
        },
        fill: {
          opacity: 1
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
    
    };
  }

  


  render() {
    return (
      <>
        <Header />
        {/* Page content */}
        <Container className="mt--7" fluid>
          <Row>
          
          <Col className="mb-5 mb-xl-0" xl="7">
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
                  <Chart options={this.state.systemLoadOptions} series={this.state.systemLoadSeries} type="line" width={900} height={545} />

                </CardBody>
              </Card>
            </Col>
            
            <Col className="mb-5 mb-xl-0" xl="5">
              <Card className="bg-secondary shadow">
                <CardHeader className="bg-white border-0">
                  <Row className="align-items-center">
                    <Col xs="8">
                      <h3 className="mb-0">Constraints and Alert Settings</h3>
                    </Col>
                    <Col className="text-right" xs="4">
                      <Button
                        color="primary"
                        href="#pablo"
                        onClick={e => e.preventDefault()}
                        size="md"
                      >
                        Save
                      </Button>
                    </Col>
                  </Row>
                </CardHeader>
                <CardBody>
                  <Form>
                    <h4 className=" text-muted mb-4">
                      Nominal Transformer Capacity
                    </h4>
                    <div className="pl-lg-4">
                      <Row>
                        <Col lg="6">
                          <FormGroup>
                            <label
                              className="form-control-label"
                              htmlFor="input-username"
                            >
                              Day
                            </label>
                            <Input
                              className="form-control-alternative"
                              id="input-username"
                              placeholder="100 kW"
                              type="text"
                            />
                          </FormGroup>
                        </Col>
                        <Col lg="6">
                          <FormGroup>
                            <label
                              className="form-control-label"
                              htmlFor="input-email"
                            >
                              Night
                            </label>
                            <Input
                              className="form-control-alternative"
                              id="input-email"
                              placeholder="200 kW"
                              type="text"
                            />
                          </FormGroup>
                        </Col>
                      </Row>
                      
                    </div>
                    <hr className="my-4" />
                    {/* Address */}
                    <h4 className=" text-muted mb-4">
                      Alerts
                    </h4>
                    <div className="pl-lg-4">
                      <Row>
                        <Col md="6">
                          <FormGroup>
                            <label
                              className="form-control-label"
                              htmlFor="input-address"
                            >
                              Yellow Load Alarm
                            </label>
                            <Input
                              className="form-control-alternative"
                              defaultValue="140%"
                              id="input-address"
                              placeholder="140%"
                              type="text"
                            />
                          </FormGroup>
                        </Col>
                      </Row>
                      <Row>
                        <Col md="6">
                          <FormGroup>
                            <label
                              className="form-control-label"
                              htmlFor="input-address"
                            >
                              Red Load Alarm
                            </label>
                            <Input
                              className="form-control-alternative"
                              defaultValue="160%"
                              id="input-address"
                              placeholder="160%"
                              type="text"
                            />
                          </FormGroup>
                        </Col>
                      </Row>
                      <Row>
                        <Col md="6">
                          <FormGroup>
                            <label
                              className="form-control-label"
                              htmlFor="input-address"
                            >
                              Resource Depletion (Battery)
                            </label>
                            <Input
                              className="form-control-alternative"
                              defaultValue="1 Hour"
                              id="input-address"
                              placeholder="1 Hour"
                              type="text"
                            />
                          </FormGroup>
                        </Col>
                      </Row>
                      
                    </div>
                    
                  </Form>
                </CardBody>
              </Card>
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
                  <Chart options={this.state.resourcesOptions} series={this.state.resourcesSeries} type="bar" width={1000} height={500} />

                </CardBody>
                
              </Card>
            </Col>
            <Col xl="4">
              <Card className="shadow">
                <CardHeader className="bg-transparent">
                  <Row className="align-items-center">
                    <div className="col">
                      <h3 className="mb-0">Other Controls</h3>
                    </div>
                  </Row>
                </CardHeader>
                <CardBody>
                <Col className="mb-5 mb-xl-0" xl="8">
                  <Row className="mt-3"><h3 className="mb-0">Cost minimizztion&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</h3><Switch checked={true}/></Row>
                  <Row className="mt-3"><h3 className="mb-0">Cost and CO2 minimizztion&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</h3><Switch checked={true}/></Row>
                  <Row className="mt-3"><h3 className="mb-0">Transformer compacity limit&nbsp;&nbsp;&nbsp;</h3><Switch checked={true}/></Row>

                </Col>
                  
                  {/* Chart */}
                  {/* <Chart options={this.state.resourcesOptions} series={this.state.resourcesSeries} type="column" width={500} height={190} /> */}
                  

                </CardBody>
              </Card>
              
            </Col>
          </Row>
        </Container>
      </>
    );
  }
}

export default PowerDispatch;
