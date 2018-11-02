import * as React from 'react';
import { Col, Container, Row  } from 'reactstrap';

import fistSvg from './fist.svg';

import './App.css';

const app = () => {
  return (
    <Container className="flex-container">
      <Row>
        <Col>
          <img id="fade-in" className="image" src={fistSvg} alt="fist" />
        </Col>
      </Row>
      <Row>
        <Col>
          <span id="fade-in" className="title">JD</span>
        </Col>
      </Row>
    </Container>
  );
};

export default app;
