import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './App.css'; // This applies the "SaaS" styles we just added

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);