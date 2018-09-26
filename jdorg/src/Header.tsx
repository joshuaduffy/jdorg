import * as React from 'react';

import logoSvg from './logo.svg';

interface IHeaderProps {
  title: string;
}

const header = (props:IHeaderProps) => {
  return (
    <header className="App-header">
    <img src={logoSvg} className="App-logo" alt="logo" />
    <h1 className="App-title">{props.title}</h1>
    </header>
  );
};

export default header;
