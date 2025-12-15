import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; 

// Environment Helper: 
// Locally, this is empty (uses package.json proxy). 
// In Production (Vercel), this reads your REACT_APP_API_URL variable.
const API_URL = process.env.REACT_APP_API_URL || "";

function App() {
  // --- 1. STATE MANAGEMENT ---
  
  // Auth State (Initialize from LocalStorage to persist on refresh)
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [username, setUsername] = useState(localStorage.getItem('username') || '');

  // Data State
  const [subscription, setSubscription] = useState(null);
  const [payments, setPayments] = useState([]);
  
  // Input State
  const [inputUsername, setInputUsername] = useState('');
  const [inputPassword, setInputPassword] = useState('');
  const [mpesaPhone, setMpesaPhone] = useState('');
  
  // UI State
  const [activeView, setActiveView] = useState('dashboard'); // 'dashboard' or 'history'
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  // --- 2. EFFECTS ---

  // Load data whenever the token changes (e.g., on login or refresh)
  useEffect(() => {
    if (token) {
      fetchData(token);
    }
  }, [token]);

  // --- 3. API ACTIONS ---

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ text: '', type: '' });

    try {
      // POST to Django Backend
      const res = await axios.post(`${API_URL}/api/auth/login/`, { 
        username: inputUsername, 
        password: inputPassword 
      });
      
      const accessToken = res.data.access;
      
      // Save to LocalStorage
      localStorage.setItem('token', accessToken);
      localStorage.setItem('username', inputUsername);
      
      // Update State
      setToken(accessToken);
      setUsername(inputUsername);
    } catch (err) {
      setMessage({ text: 'Invalid Username or Password', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    // Clear LocalStorage
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    
    // Reset State
    setToken(null);
    setUsername('');
    setSubscription(null);
    setPayments([]);
    setInputUsername('');
    setInputPassword('');
  };

  const fetchData = (authToken) => {
    // 1. Fetch Subscription
    axios.get(`${API_URL}/api/billing/subscriptions/`, { 
      headers: { Authorization: `Bearer ${authToken}` } 
    })
    .then(res => {
      if (res.data.length > 0) {
        setSubscription(res.data[0]);
      }
    })
    .catch(err => {
      // If token is invalid (401), force logout
      if (err.response && err.response.status === 401) {
        handleLogout();
      }
      console.error(err);
    });

    // 2. Fetch Payment History
    axios.get(`${API_URL}/api/billing/payments/`, { 
      headers: { Authorization: `Bearer ${authToken}` } 
    })
    .then(res => setPayments(res.data))
    .catch(err => console.error(err));
  };

  const handlePayment = async () => {
    if (!subscription || !mpesaPhone) return;
    
    setIsLoading(true);
    setMessage({ text: 'Sending STK Push to your phone...', type: 'warning' });

    try {
      await axios.post(`${API_URL}/api/mpesa/pay/`, {
        phone: mpesaPhone,
        amount: subscription.price 
      }, { 
        headers: { Authorization: `Bearer ${token}` } 
      });
      
      setMessage({ text: 'Success! Check your phone to enter PIN.', type: 'success' });
    } catch (err) {
      setMessage({ text: 'Payment Failed. Check phone number.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // --- 4. RENDER: LOGIN SCREEN ---
  
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
                value={inputUsername}
                onChange={e => setInputUsername(e.target.value)} 
                placeholder="e.g. john_doe" 
              />
            </div>
            <div>
              <label>Password</label>
              <input 
                type="password" 
                value={inputPassword}
                onChange={e => setInputPassword(e.target.value)} 
                placeholder="••••••••" 
              />
            </div>
            
            {message.text && (
              <div style={{
                marginBottom: '15px', 
                color: message.type === 'error' ? 'red' : 'green', 
                textAlign: 'center'
              }}>
                {message.text}
              </div>
            )}

            <button type="submit" className="btn-primary" disabled={isLoading}>
              {isLoading ? 'Securely Logging in...' : 'Login to Account'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // --- 5. RENDER: MAIN APP ---

  return (
    <div className="app-layout">
      {/* SIDEBAR */}
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

      {/* MAIN CONTENT AREA */}
      <main className="main-content">
        <header className="header">
          <h1>{activeView === 'dashboard' ? 'Overview' : 'Transaction History'}</h1>
          <div className="user-info">
            Logged in as <strong>{username}</strong>
          </div>
        </header>

        {/* VIEW 1: DASHBOARD */}
        {activeView === 'dashboard' && (
          <>
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Current Plan</h3>
                <div className="value">{subscription ? subscription.package_name : 'No Plan'}</div>
                <div style={{marginTop:'10px', color: subscription?.is_active ? 'green' : 'red', fontWeight: 'bold'}}>
                  {subscription?.is_active ? '● Online' : '● Inactive'}
                </div>
              </div>
              <div className="stat-card">
                <h3>Download Speed</h3>
                <div className="value">{subscription ? subscription.speed + ' Mbps' : '0 Mbps'}</div>
              </div>
              <div className="stat-card">
                <h3>Renewal Date</h3>
                <div className="value" style={{fontSize: '1.2rem'}}>
                  {subscription ? new Date(subscription.end_date).toDateString() : '--'}
                </div>
              </div>
            </div>

            {/* QUICK PAY SECTION */}
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

        {/* VIEW 2: HISTORY */}
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
                  <tr>
                    <td colSpan="4" style={{textAlign:'center', padding:'2rem', color: '#6b7280'}}>
                      No transactions found.
                    </td>
                  </tr>
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