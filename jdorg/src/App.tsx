import * as React from 'react';

import fistSvg from './fist.svg';

import './App.scss';

const app = () => {
  return (
    <div className="flex-container">
      <img id="fade-in" className="image" src={fistSvg} alt="fist" />
      <span id="fade-in" className="title">JD</span>
    </div>
  );
};

export default app;
