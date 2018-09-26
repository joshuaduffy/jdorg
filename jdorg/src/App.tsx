import * as React from 'react';

import { getTitleApi } from './Api';
import Header from './Header';

import './App.css';

interface IAppState {
  title: string;
}

class App extends React.Component<{}, IAppState> {
  public constructor(props:any) {
    super(props);
    this.state = {
      title: 'Loading',
    };
  }

  public componentDidMount() {
    getTitleApi().then(
      (resp) => {
        const title = resp.data.title;
        this.setState({ title });
      },
    );
  }

  public render() {
    return (
      <div className="App">
        <Header title={this.state.title} />
        <p className="App-intro">
          To get started, edit <code>src/App.tsx</code> and save to reload.
        </p>
      </div>
    );
  }
}

export default App;
