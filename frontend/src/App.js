import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; 

// Environment Helper
const API_URL = process.env.REACT_APP_API_URL || "";

function App() {
  // --- 1. STATE MANAGEMENT ---
  
  // Auth State
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [username, setUsername] = useState(localStorage.getItem('username') || '');

  // UI State
  const [activeView, setActiveView] = useState('dashboard');
  const [isRegistering, setIsRegistering] = useState(false); // New: Toggle Login/Register
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  // Data State
  const [subscription, setSubscription] = useState(null);
  const [payments, setPayments] = useState([]);
  
  // Login Inputs
  const [inputUsername, setInputUsername] = useState('');
  const [inputPassword, setInputPassword] = useState('');

  // Register Inputs (New)
  const [regUsername, setRegUsername] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPhone, setRegPhone] = useState('');
  
  // Payment Input
  const [mpesaPhone, setMpesaPhone] = useState('');

  // --- 2. EFFECTS ---
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
      const res = await axios.post(`${API_URL}/api/auth/login/`, { 
        username: inputUsername, 
        password: inputPassword 
      });
      
      const accessToken = res.data.access;
      localStorage.setItem('token', accessToken);
      localStorage.setItem('username', inputUsername);
      setToken(accessToken);
      setUsername(inputUsername);
    } catch (err) {
      setMessage({ text: 'Invalid Username or Password', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // New: Handle Registration
  const handleRegister = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ text: '', type: '' });

    try {
      await axios.post(`${API_URL}/api/users/register/`, {
        username: regUsername,
        password: regPassword,
        email: regEmail,
        phone_number: regPhone
      });
      
      setMessage({ text: 'Account created! Please log in.', type: 'success' });
      setIsRegistering(false); // Switch back to login view
      setInputUsername(regUsername); // Auto-fill username
    } catch (err) {
      console.error(err);
      setMessage({ text: 'Registration failed. Username may be taken.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setToken(null);
    setUsername('');
    setSubscription(null);
    setPayments([]);
  };

  const fetchData = (authToken) => {
    // Fetch Subscription
    axios.get(`${API_URL}/api/billing/subscriptions/`, { 
      headers: { Authorization: `Bearer ${authToken}` } 
    })
    .then(res => { if (res.data.length > 0) setSubscription(res.data[0]); })
    .catch(err => { if (err.response?.status === 401) handleLogout(); });

    // Fetch History
    axios.get(`${API_URL}/api/billing/payments/`, { 
      headers: { Authorization: `Bearer ${authToken}` } 
    })
    .then(res => setPayments(res.data))
    .catch(console.error);
  };

  const handlePayment = async () => {
    if (!subscription || !mpesaPhone) return;
    setIsLoading(true);
    setMessage({ text: 'Sending STK Push...', type: 'warning' });

    try {
      await axios.post(`${API_URL}/api/mpesa/pay/`, {
        phone: mpesaPhone,
        amount: subscription.price 
      }, { headers: { Authorization: `Bearer ${token}` } });
      setMessage({ text: 'Success! Check your phone.', type: 'success' });
    } catch (err) {
      setMessage({ text: 'Payment Failed.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // --- 4. RENDER: AUTH SCREEN (Login / Register) ---
  
  if (!token) {
    return (
      <div className="login-container">
        <div className="login-card">
          <h2>{isRegistering ? 'Create Account' : 'ISP Customer Portal'}</h2>
          
          {/* LOGIN FORM */}
          {!isRegistering ? (
            <form onSubmit={handleLogin}>
              <div>
                <label>Username</label>
                <input type="text" onChange={e => setInputUsername(e.target.value)} value={inputUsername} required />
              </div>
              <div>
                <label>Password</label>
                <input type="password" onChange={e => setInputPassword(e.target.value)} value={inputPassword} required />
              </div>
              
              {message.text && <p className={`msg-${message.type}`} style={{color: message.type==='error'?'red':'green', textAlign:'center'}}>{message.text}</p>}
              
              <button type="submit" className="btn-primary" disabled={isLoading}>
                {isLoading ? 'Logging in...' : 'Login to Account'}
              </button>
              
              <p style={{marginTop: '15px', textAlign: 'center', fontSize: '0.9rem'}}>
                New user? <span style={{color: '#2563eb', cursor: 'pointer', fontWeight: 'bold'}} onClick={() => {setIsRegistering(true); setMessage({text:'', type:''})}}>Create an account</span>
              </p>
            </form>
          ) : (
            
            /* REGISTER FORM */
            <form onSubmit={handleRegister}>
              <div>
                <label>Username</label>
                <input type="text" onChange={e => setRegUsername(e.target.value)} required />
              </div>
              <div>
                <label>Email (Optional)</label>
                <input type="email" onChange={e => setRegEmail(e.target.value)} />
              </div>
              <div>
                <label>Phone Number</label>
                <input type="text" placeholder="2547..." onChange={e => setRegPhone(e.target.value)} required />
              </div>
              <div>
                <label>Password</label>
                <input type="password" onChange={e => setRegPassword(e.target.value)} required />
              </div>

              {message.text && <p className={`msg-${message.type}`} style={{color: message.type==='error'?'red':'green', textAlign:'center'}}>{message.text}</p>}

              <button type="submit" className="btn-primary" disabled={isLoading}>
                {isLoading ? 'Creating...' : 'Sign Up'}
              </button>

              <p style={{marginTop: '15px', textAlign: 'center', fontSize: '0.9rem'}}>
                Already have an account? <span style={{color: '#2563eb', cursor: 'pointer', fontWeight: 'bold'}} onClick={() => {setIsRegistering(false); setMessage({text:'', type:''})}}>Log In</span>
              </p>
            </form>
          )}
        </div>
      </div>
    );
  }

  // --- 5. RENDER: MAIN APP ---
  // (This part remains the same as your previous working version)
  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand-logo"><span>📡 WiFi Portal</span></div>
        <nav className="nav-links">
          <div className={`nav-item ${activeView === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveView('dashboard')}>📊 My Dashboard</div>
          <div className={`nav-item ${activeView === 'history' ? 'active' : ''}`} onClick={() => setActiveView('history')}>💳 Payment History</div>
        </nav>
        <div className="logout-btn" onClick={handleLogout}>Sign Out</div>
      </aside>

      <main className="main-content">
        <header className="header">
          <h1>{activeView === 'dashboard' ? 'Overview' : 'Transaction History'}</h1>
          <div className="user-info">Logged in as <strong>{username}</strong></div>
        </header>

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
                <h3>Speed</h3>
                <div className="value">{subscription ? subscription.speed + ' Mbps' : '0 Mbps'}</div>
              </div>
              <div className="stat-card">
                <h3>Renewal</h3>
                <div className="value">{subscription ? new Date(subscription.end_date).toDateString() : '--'}</div>
              </div>
            </div>

            <div className="table-container">
              <div className="table-header"><h3>Quick Top-Up</h3></div>
              <div style={{padding: '2rem', maxWidth: '500px'}}>
                <p style={{marginBottom: '1rem', color: '#6b7280'}}>Enter M-Pesa number to pay.</p>
                <input type="text" placeholder="2547XXXXXXXX" value={mpesaPhone} onChange={e => setMpesaPhone(e.target.value)}/>
                {message.text && <div style={{padding: '10px', marginTop:'10px', borderRadius: '6px', backgroundColor: message.type === 'success' ? '#d1fae5' : '#fee2e2', color: message.type === 'success' ? '#065f46' : '#991b1b'}}>{message.text}</div>}
                <button className="btn-primary" onClick={handlePayment} disabled={isLoading || !subscription} style={{marginTop:'10px'}}>
                  {isLoading ? 'Processing...' : `Pay KES ${subscription ? subscription.price : '0'} Now`}
                </button>
              </div>
            </div>
          </>
        )}

        {activeView === 'history' && (
          <div className="table-container">
            <table>
              <thead><tr><th>Date</th><th>Receipt</th><th>Amount</th><th>Status</th></tr></thead>
              <tbody>
                {payments.map((pay) => (
                  <tr key={pay.id}>
                    <td>{new Date(pay.created_at).toLocaleDateString()}</td>
                    <td>{pay.mpesa_receipt_number || '---'}</td>
                    <td>KES {pay.amount}</td>
                    <td>{pay.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;