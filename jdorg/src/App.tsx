import * as React from 'react';
import fistSvg from './fist.svg';

import './App.css';

const app = () => {
  return (
    <div className="flex-container">
      <img className="image" src={fistSvg} alt="fist" />
      <span className="title">JD</span>
    </div>
  );
};

export default app;
