import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [token, setToken] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  // 1. The Login Function
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // Connects to YOUR Django Backend
      const res = await axios.post('http://127.0.0.1:8000/api/auth/login/', {
        username,
        password
      });
      setToken(res.data.access);
      fetchSubscription(res.data.access);
    } catch (err) {
      alert("Invalid Credentials");
    }
  };

  // 2. Fetch Data (Only for this specific user)
  const fetchSubscription = async (authToken) => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/billing/subscriptions/', {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      // Get the first active subscription
      setSubscription(res.data[0]); 
    } catch (err) {
      console.error(err);
    }
  };

  if (!token) {
    return (
      <div style={{ padding: '50px', textAlign: 'center' }}>
        <h2>Customer Portal Login</h2>
        <form onSubmit={handleLogin}>
          <input placeholder="Username" onChange={e => setUsername(e.target.value)} /><br/>
          <input type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} /><br/>
          <button type="submit">Login</button>
        </form>
      </div>
    );
  }

  return (
    <div style={{ padding: '50px', fontFamily: 'Arial' }}>
      <h1>Welcome, {username}</h1>
      <hr />
      
      {subscription ? (
        <div style={{ border: '1px solid #ccc', padding: '20px', borderRadius: '10px' }}>
          <h3>Your Plan: {subscription.package_name}</h3>
          <p>Speed: {subscription.speed} Mbps</p>
          <p>Expires: {new Date(subscription.end_date).toDateString()}</p>
          <p>Status: <b style={{color: 'green'}}>Active</b></p>
        </div>
      ) : (
        <p>You have no active plan. Please pay via M-Pesa.</p>
      )}
    </div>
  );
}

export default App;