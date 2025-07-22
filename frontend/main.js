import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';

function App() {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await axios.post('/codex', { prompt });
    setResult(res.data.result);
  };

  return (
    <div>
      <h1>OpenAI Codex Web</h1>
      <form onSubmit={handleSubmit}>
        <textarea value={prompt} onChange={e => setPrompt(e.target.value)} rows={5} cols={50} />
        <br />
        <button type="submit">Submit</button>
      </form>
      <h2>Result:</h2>
      <pre>{result}</pre>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
