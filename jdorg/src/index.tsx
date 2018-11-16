// tslint:disable-next-line:import-name
import React from 'react';
import reactDom from 'react-dom';
import App from './App';
import './index.scss';
import * as serviceWorker from './serviceWorker';

reactDom.render(<App />, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: http://bit.ly/CRA-PWA
serviceWorker.unregister();
