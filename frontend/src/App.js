import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; 

function App() {
  // 1. Initialize State from Local Storage (Fixes the refresh issue)
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [username, setUsername] = useState(localStorage.getItem('username') || '');
  
  const [subscription, setSubscription] = useState(null);
  const [payments, setPayments] = useState([]);
  
  // Login Inputs
  const [inputUsername, setInputUsername] = useState('');
  const [inputPassword, setInputPassword] = useState('');
  
  // Payment Input
  const [mpesaPhone, setMpesaPhone] = useState('');
  
  // UI States
  const [activeView, setActiveView] = useState('dashboard'); 
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  // 2. Fetch Data Automatically on App Load (if token exists)
  useEffect(() => {
    if (token) {
      fetchData(token);
    }
  }, [token]);

  // --- API LOGIC ---

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await axios.post('/api/auth/login/', { 
        username: inputUsername, 
        password: inputPassword 
      });
      
      const accessToken = res.data.access;
      
      // SAVE TO LOCAL STORAGE
      localStorage.setItem('token', accessToken);
      localStorage.setItem('username', inputUsername);
      
      setToken(accessToken);
      setUsername(inputUsername);
      setMessage({ text: '', type: '' });
    } catch (err) {
      setMessage({ text: 'Invalid Credentials', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    // CLEAR LOCAL STORAGE
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setToken(null);
    setUsername('');
    setSubscription(null);
    setPayments([]);
  };

  const fetchData = (authToken) => {
    // 1. Get Subscriptions
    axios.get('/api/billing/subscriptions/', { headers: { Authorization: `Bearer ${authToken}` } })
      .then(res => { if (res.data.length > 0) setSubscription(res.data[0]); })
      .catch(err => {
        // If token is expired (401), log them out automatically
        if (err.response && err.response.status === 401) {
          handleLogout();
        }
        console.error(err);
      });

    // 2. Get History
    axios.get('/api/billing/payments/', { headers: { Authorization: `Bearer ${authToken}` } })
      .then(res => setPayments(res.data))
      .catch(err => console.error(err));
  };

  const handlePayment = async () => {
    if (!subscription || !mpesaPhone) return;
    setIsLoading(true);
    setMessage({ text: 'Initiating STK Push...', type: 'warning' });

    try {
      await axios.post('/api/mpesa/pay/', {
        phone: mpesaPhone,
        amount: subscription.price 
      }, { headers: { Authorization: `Bearer ${token}` } });
      setMessage({ text: 'Check your phone for the PIN prompt!', type: 'success' });
    } catch (err) {
      setMessage({ text: 'Payment Failed to Initiate.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // --- LOGIN SCREEN ---
  if (!token) {
    return (
      <div className="login-container">
        <div className="login-card">
          <h2>ISP Customer Portal</h2>
          <form onSubmit={handleLogin}>
            <div>
              <label>Username</label>
              <input 
                type="text" 
                onChange={e => setInputUsername(e.target.value)} 
                placeholder="e.g. john_doe" 
              />
            </div>
            <div>
              <label>Password</label>
              <input 
                type="password" 
                onChange={e => setInputPassword(e.target.value)} 
                placeholder="••••••••" 
              />
            </div>
            {message.text && <p style={{color: message.type === 'error' ? 'red' : 'green', textAlign:'center', marginBottom:'10px'}}>{message.text}</p>}
            <button type="submit" className="btn-primary" disabled={isLoading}>
              {isLoading ? 'Accessing...' : 'Login to Account'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // --- MAIN APP LAYOUT ---
  return (
    <div className="app-layout">
      {/* 1. SIDEBAR */}
      <aside className="sidebar">
        <div className="brand-logo">
           <span>📡 WiFi Portal</span>
        </div>
        
        <nav className="nav-links">
          <div 
            className={`nav-item ${activeView === 'dashboard' ? 'active' : ''}`} 
            onClick={() => setActiveView('dashboard')}
          >
            📊 My Dashboard
          </div>
          <div 
            className={`nav-item ${activeView === 'history' ? 'active' : ''}`} 
            onClick={() => setActiveView('history')}
          >
            💳 Payment History
          </div>
        </nav>

        <div className="logout-btn" onClick={handleLogout}>
          Sign Out
        </div>
      </aside>

      {/* 2. MAIN CONTENT */}
      <main className="main-content">
        <header className="header">
          <h1>{activeView === 'dashboard' ? 'Overview' : 'Transaction History'}</h1>
          <div className="user-info">Logged in as <strong>{username}</strong></div>
        </header>

        {/* VIEW: DASHBOARD */}
        {activeView === 'dashboard' && (
          <>
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Current Plan</h3>
                <div className="value">{subscription ? subscription.package_name : 'No Plan'}</div>
                <div style={{marginTop:'10px', color: subscription?.is_active ? 'green' : 'red'}}>
                  {subscription?.is_active ? '● Online' : '● Inactive'}
                </div>
              </div>
              <div className="stat-card">
                <h3>Speed Limit</h3>
                <div className="value">{subscription ? subscription.speed + ' Mbps' : '0 Mbps'}</div>
              </div>
              <div className="stat-card">
                <h3>Renewal Date</h3>
                <div className="value" style={{fontSize: '1.2rem'}}>
                  {subscription ? new Date(subscription.end_date).toDateString() : '--'}
                </div>
              </div>
            </div>

            {/* Quick Pay Section */}
            <div className="table-container">
              <div className="table-header">
                <h3>Quick Top-Up</h3>
              </div>
              <div style={{padding: '2rem', maxWidth: '500px'}}>
                <p style={{marginBottom: '1rem', color: '#6b7280'}}>
                  Enter your M-Pesa number below to renew your <b>{subscription?.package_name}</b> plan instantly.
                </p>
                <label>M-Pesa Number</label>
                <input 
                  type="text" 
                  placeholder="2547XXXXXXXX" 
                  value={mpesaPhone}
                  onChange={e => setMpesaPhone(e.target.value)}
                />
                
                {message.text && (
                  <div style={{
                    padding: '10px', 
                    marginBottom: '15px', 
                    borderRadius: '6px',
                    backgroundColor: message.type === 'success' ? '#d1fae5' : '#fee2e2',
                    color: message.type === 'success' ? '#065f46' : '#991b1b'
                  }}>
                    {message.text}
                  </div>
                )}

                <button className="btn-primary" onClick={handlePayment} disabled={isLoading || !subscription}>
                  {isLoading ? 'Processing Payment...' : `Pay KES ${subscription ? subscription.price : '0'} Now`}
                </button>
              </div>
            </div>
          </>
        )}

        {/* VIEW: HISTORY */}
        {activeView === 'history' && (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Receipt No</th>
                  <th>Amount</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {payments.length > 0 ? payments.map((pay) => (
                  <tr key={pay.id}>
                    <td>{new Date(pay.created_at).toLocaleDateString()}</td>
                    <td style={{fontFamily: 'monospace'}}>{pay.mpesa_receipt_number || '---'}</td>
                    <td>KES {pay.amount}</td>
                    <td>
                      <span className={`badge ${
                        pay.status === 'COMPLETED' ? 'badge-success' : 
                        pay.status === 'PENDING' ? 'badge-warning' : 'badge-danger'
                      }`}>
                        {pay.status}
                      </span>
                    </td>
                  </tr>
                )) : (
                  <tr><td colSpan="4" style={{textAlign:'center', padding:'2rem'}}>No transactions found.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;