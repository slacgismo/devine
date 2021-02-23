import React from "react";
import Checkbox from '@material-ui/core/Checkbox';
import { withStyles } from '@material-ui/core/styles';

import { green } from '@material-ui/core/colors';
// reactstrap components
import {
  Badge,
  Card,
  CardHeader,
  CardFooter,
  DropdownMenu,
  DropdownItem,
  UncontrolledDropdown,
  DropdownToggle,
  Media,
  Pagination,
  PaginationItem,
  PaginationLink,
  Progress,
  Table,
  Container,
  Row,
  UncontrolledTooltip,
  Button,
  Col,
  Form,
  FormGroup,
  InputGroupAddon,
  InputGroupText,
  Input,
  InputGroup,
} from "reactstrap";
// core components
import Header from "components/Headers/Header.js";

const GreenCheckbox = withStyles({
  root: {
    color: green[400],
    '&$checked': {
      color: green[600],
    },
  },
  checked: {},
})((props) => <Checkbox color="default" {...props} />);

class Notifications extends React.Component {
  render() {
    return (
      <>
        <Header />
        {/* Page content */}
        <Container className="mt--7" fluid>
          {/* Table */}
          <Row>
          <Col className="mb-5 mb-xl-0" xl="6">
          <div className="col">
            
            <Card className="shadow">
              <CardHeader className="border-0">
              <Row className="align-items-center">
                <Col xs="6">
                      <h3 className="mb-0">Alerts</h3>
                    </Col>
                    <Col className="text-right" xs="4">
                    <Form className="form-inline mr-3 d-none d-md-flex ml-lg-auto">
                      <FormGroup className="mb-0">
                        <InputGroup className="input-group-alternative">
                          <InputGroupAddon addonType="prepend">
                            <InputGroupText>
                              <i className="fas fa-search" />
                            </InputGroupText>
                          </InputGroupAddon>
                          <Input placeholder="Search" type="text" />
                        </InputGroup>
                      </FormGroup>
                    </Form>
                    </Col>
                    <Col className="text-right" xs="2">
                      <Button
                        color="primary"
                        href="#pablo"
                        onClick={e => e.preventDefault()}
                        size="md"
                      >
                        Download
                      </Button>
                    </Col>
                </Row>
              
              </CardHeader>
              <Table className="align-items-center table-flush" responsive>
                <thead className="thead-light">
                  <tr>
                    <th scope="col">Date</th>
                    <th scope="col">Time</th>
                    <th scope="col">Type</th>
                    <th scope="col">Description</th>
                    <th scope="col">Status</th>
                    <th scope="col" />
                  </tr>
                </thead>
                <tbody>
                  <tr>
                  <td >
                          <span className="mb-0 text-sm">
                          11/20/2020
                          </span>

                    </td>
                    <td>5:50</td>
                    <td>
                      Price Alert
                    </td>
                    <td>
                    Lorem ipsum dolor sit amet
                    </td>
                    <td>
                    <Badge color="" className="badge-dot mr-4">
                        <i className="bg-warning" />
                        pending
                      </Badge>                 
                    </td>

                  </tr>
                  
                  <tr>
                  <td >
                          <span className="mb-0 text-sm">
                          11/20/2020
                          </span>

                    </td>
                    <td>3:51</td>
                    <td>
                      Resource Depletion
                    </td>
                    <td>
                    Lorem ipsum dolor sit amet
                    </td>
                    <td>
                    <Badge color="" className="badge-dot">
                        <i className="bg-info" />
                        Open
                      </Badge>
                    </td>

                  </tr>
                  <tr>
                    <td >
                          <span className="mb-0 text-sm">
                          11/20/2020
                          </span>

                    </td>
                    <td>14:20</td>
                    <td>
                      Capacity Bounds
                    </td>
                    <td>
                    Lorem ipsum dolor sit amet
                    </td>
                    <td>
                    <Badge color="" className="badge-dot mr-4">
                        <i className="bg-success" />
                        Resolved
                      </Badge>
                    </td>

                  </tr>
                  <tr>
                  <td >
                          <span className="mb-0 text-sm">
                          11/20/2020
                          </span>

                    </td>
                    <td>5:50</td>
                    <td>
                      Price Alert
                    </td>
                    <td>
                    Lorem ipsum dolor sit amet
                    </td>
                    <td>
                    <Badge color="" className="badge-dot mr-4">
                        <i className="bg-warning" />
                        pending
                      </Badge>                 
                    </td>

                  </tr>
                  
                  <tr>
                  <td >
                          <span className="mb-0 text-sm">
                          11/20/2020
                          </span>

                    </td>
                    <td>3:51</td>
                    <td>
                      Resource Depletion
                    </td>
                    <td>
                    Lorem ipsum dolor sit amet
                    </td>
                    <td>
                    <Badge color="" className="badge-dot">
                        <i className="bg-info" />
                        Open
                      </Badge>
                    </td>

                  </tr>
                  <tr>
                    <td >
                          <span className="mb-0 text-sm">
                          11/20/2020
                          </span>

                    </td>
                    <td>14:20</td>
                    <td>
                      Capacity Bounds
                    </td>
                    <td>
                    Lorem ipsum dolor sit amet
                    </td>
                    <td>
                    <Badge color="" className="badge-dot mr-4">
                        <i className="bg-success" />
                        Resolved
                      </Badge>
                    </td>

                  </tr>
                  <tr>
                  <td >
                          <span className="mb-0 text-sm">
                          11/20/2020
                          </span>

                    </td>
                    <td>5:50</td>
                    <td>
                      Price Alert
                    </td>
                    <td>
                    Lorem ipsum dolor sit amet
                    </td>
                    <td>
                    <Badge color="" className="badge-dot mr-4">
                        <i className="bg-warning" />
                        pending
                      </Badge>                 
                    </td>

                  </tr>
                  
                  <tr>
                  <td >
                          <span className="mb-0 text-sm">
                          11/20/2020
                          </span>

                    </td>
                    <td>3:51</td>
                    <td>
                      Resource Depletion
                    </td>
                    <td>
                    Lorem ipsum dolor sit amet
                    </td>
                    <td>
                    <Badge color="" className="badge-dot">
                        <i className="bg-info" />
                        Open
                      </Badge>
                    </td>

                  </tr>
                  <tr>
                    <td >
                          <span className="mb-0 text-sm">
                          11/20/2020
                          </span>

                    </td>
                    <td>14:20</td>
                    <td>
                      Capacity Bounds
                    </td>
                    <td>
                    Lorem ipsum dolor sit amet
                    </td>
                    <td>
                    <Badge color="" className="badge-dot mr-4">
                        <i className="bg-success" />
                        Resolved
                      </Badge>
                    </td>

                  </tr>
                  <tr>
                  <td >
                          <span className="mb-0 text-sm">
                          11/20/2020
                          </span>

                    </td>
                    <td>5:50</td>
                    <td>
                      Price Alert
                    </td>
                    <td>
                    Lorem ipsum dolor sit amet
                    </td>
                    <td>
                    <Badge color="" className="badge-dot mr-4">
                        <i className="bg-warning" />
                        pending
                      </Badge>                 
                    </td>

                  </tr>
                  
                  <tr>
                  <td >
                          <span className="mb-0 text-sm">
                          11/20/2020
                          </span>

                    </td>
                    <td>3:51</td>
                    <td>
                      Resource Depletion
                    </td>
                    <td>
                    Lorem ipsum dolor sit amet
                    </td>
                    <td>
                    <Badge color="" className="badge-dot">
                        <i className="bg-info" />
                        Open
                      </Badge>
                    </td>

                  </tr>
                  <tr>
                    <td >
                          <span className="mb-0 text-sm">
                          11/20/2020
                          </span>

                    </td>
                    <td>14:20</td>
                    <td>
                      Capacity Bounds
                    </td>
                    <td>
                    Lorem ipsum dolor sit amet
                    </td>
                    <td>
                    <Badge color="" className="badge-dot mr-4">
                        <i className="bg-success" />
                        Resolved
                      </Badge>
                    </td>

                  </tr>
                  <tr>
                  <td >
                          <span className="mb-0 text-sm">
                          11/20/2020
                          </span>

                    </td>
                    <td>5:50</td>
                    <td>
                      Price Alert
                    </td>
                    <td>
                    Lorem ipsum dolor sit amet
                    </td>
                    <td>
                    <Badge color="" className="badge-dot mr-4">
                        <i className="bg-warning" />
                        pending
                      </Badge>                 
                    </td>

                  </tr>
                  
                  <tr>
                  <td >
                          <span className="mb-0 text-sm">
                          11/20/2020
                          </span>

                    </td>
                    <td>3:51</td>
                    <td>
                      Resource Depletion
                    </td>
                    <td>
                    Lorem ipsum dolor sit amet
                    </td>
                    <td>
                    <Badge color="" className="badge-dot">
                        <i className="bg-info" />
                        Open
                      </Badge>
                    </td>

                  </tr>
                  <tr>
                    <td >
                          <span className="mb-0 text-sm">
                          11/20/2020
                          </span>

                    </td>
                    <td>14:20</td>
                    <td>
                      Capacity Bounds
                    </td>
                    <td>
                    Lorem ipsum dolor sit amet
                    </td>
                    <td>
                    <Badge color="" className="badge-dot mr-4">
                        <i className="bg-success" />
                        Resolved
                      </Badge>
                    </td>

                  </tr>
                </tbody>
              </Table>
              
            </Card>
          </div>
          </Col>
          <Col className="mb-5 mb-xl-0" xl="6">
            <Row>
            
            <Card className="shadow">
              
              <CardHeader className="border-0">
              <Row className="align-items-center">
                    <Col xs="7">
                      <h3 className="mb-0">Notifications</h3>
                    </Col>
                    <Col className="text-right" xs="2">
                      <Button
                        color="primary"
                        href="#pablo"
                        onClick={e => e.preventDefault()}
                        size="md"
                      >
                        Add New Row
                      </Button>
                    </Col>
                    <Col className="text-right" xs="3">
                      <Button
                        color="secondary"
                        href="#pablo"
                        onClick={e => e.preventDefault()}
                        size="md"
                      >
                        Delete Selected
                      </Button>
                    </Col>
                    
                  </Row>
              </CardHeader>

              <Table className="align-items-center table-flush" responsive>
                <thead className="thead-light">
                  <tr>
                    <th scope="col">Delete</th>
                    <th scope="col">Email</th>
                    <th scope="col">Load(yellow)</th>
                    <th scope="col">Load(red)</th>
                    <th scope="col">Source Depletion</th>
                    <th scope="col">Telecomm Alerts</th>
                    <th scope="col" />
                  </tr>
                </thead>
                <tbody>
                  <tr>
                  <td className="text-center">
                    <GreenCheckbox />
                    </td>
                    <td>user1@gmail.com</td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>
                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                  </tr>
                  
                  <tr>
                  <td className="text-center">
                    <GreenCheckbox />
                    </td>
                    <td>user2@gmail.com</td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                  </tr>
                  <tr>
                  <td className="text-center">
                    <GreenCheckbox />
                    </td>
                    <td>user3@gmail.com</td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                  </tr>
                  <tr>
                  <td className="text-center">
                    <GreenCheckbox />
                    </td>
                    <td>user4@gmail.com</td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>
                    </td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                  </tr>
                  
                  <tr>
                  <td className="text-center">
                    <GreenCheckbox />
                    </td>
                    <td>user5@gmail.com</td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                  </tr>
                  <tr>
                  <td className="text-center">
                    <GreenCheckbox />
                    </td>
                    <td>user6@gmail.com</td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                  </tr>
                  <tr>
                  <td className="text-center">
                    <GreenCheckbox />
                    </td>
                    <td>user7@gmail.com</td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>
                    </td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                  </tr>
                  
                  <tr>
                  <td className="text-center">
                    <GreenCheckbox />
                    </td>
                    <td>user8@gmail.com</td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                  </tr>
                  <tr>
                  <td className="text-center">
                    <GreenCheckbox />
                    </td>
                    <td>user9@gmail.com</td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                  </tr>
                  <tr>
                  <td className="text-center">
                    <GreenCheckbox />
                    </td>
                    <td>user10@gmail.com</td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>
                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                  </tr>
                  
                  <tr>
                  <td className="text-center">
                    <GreenCheckbox />
                    </td>
                    <td>user11@gmail.com</td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                    <td className="text-center">
                    <GreenCheckbox />

                    </td>
                    <td className="text-center">
                    <GreenCheckbox checked/>

                    </td>
                  </tr>

                </tbody>
              </Table>
            </Card>
            </Row>
 
          </Col>
            
          </Row>
          {/* Dark table */}
          
        </Container>
      </>
    );
  }
}

export default Notifications;
