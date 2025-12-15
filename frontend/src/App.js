import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; 

// Environment Helper (Connects to your Render Backend)
// If running locally, this uses http://127.0.0.1:8000
const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

function App() {
  // ==========================================
  // 1. STATE MANAGEMENT
  // ==========================================
  
  // Auth State
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [username, setUsername] = useState(localStorage.getItem('username') || '');

  // UI State
  const [activeView, setActiveView] = useState('dashboard'); // 'dashboard' or 'history'
  const [isRegistering, setIsRegistering] = useState(false); // Toggle Register Form
  const [isResetting, setIsResetting] = useState(false);     // Toggle Forgot Password Form (false, true, or 'confirm')
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  // Data State
  const [subscription, setSubscription] = useState(null);
  const [payments, setPayments] = useState([]);
  
  // Login Inputs
  const [inputUsername, setInputUsername] = useState('');
  const [inputPassword, setInputPassword] = useState('');

  // Register Inputs
  const [regUsername, setRegUsername] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPhone, setRegPhone] = useState('');

  // Password Reset Inputs
  const [resetEmail, setResetEmail] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  
  // Payment Input
  const [mpesaPhone, setMpesaPhone] = useState('');

  // ==========================================
  // 2. EFFECTS (Load Data on Login)
  // ==========================================
  useEffect(() => {
    if (token) {
      fetchData(token);
    }
  }, [token]);

  // ==========================================
  // 3. API ACTIONS
  // ==========================================

  // --- LOGIN ---
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

  // --- REGISTER ---
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
      setIsRegistering(false); // Switch back to login
      setInputUsername(regUsername);
    } catch (err) {
      // Improved Error Handling
      let errorMsg = "Registration failed.";
      if (err.response && err.response.data) {
        if (err.response.data.username) errorMsg = `Username: ${err.response.data.username[0]}`;
        else if (err.response.data.password) errorMsg = `Password: ${err.response.data.password[0]}`;
        else if (err.response.data.phone_number) errorMsg = `Phone: ${err.response.data.phone_number[0]}`;
      }
      setMessage({ text: errorMsg, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // --- FORGOT PASSWORD (STEP 1: Request Email) ---
  const handleRequestReset = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ text: 'Sending email...', type: 'warning' });
    try {
      // Note: This endpoint comes from django-rest-passwordreset
      await axios.post(`${API_URL}/api/users/password_reset/`, { email: resetEmail });
      setMessage({ text: 'Check your email for the reset token!', type: 'success' });
      setIsResetting('confirm'); // Move to Step 2
    } catch (err) {
      console.error("Reset Error:", err);
      // DEBUG: Show exact error from server
      let errorMsg = "Email not found or server error.";
      if (err.response && err.response.data) {
          // Sometimes the error is an object { email: ["..."] }
          if (err.response.data.email) {
              errorMsg = err.response.data.email[0];
          } 
          // Sometimes it is just a detail message
          else if (err.response.data.detail) {
              errorMsg = err.response.data.detail;
          }
      }
      if (err.response && err.response.status === 500) {
          errorMsg = "Server Error (500). Check Backend Logs (Email Settings might be wrong).";
      }
      setMessage({ text: errorMsg, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // --- FORGOT PASSWORD (STEP 2: Confirm New Password) ---
  const handleConfirmReset = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await axios.post(`${API_URL}/api/users/password_reset/confirm/`, {
        token: resetToken,
        password: newPassword
      });
      setMessage({ text: 'Password changed successfully! Please login.', type: 'success' });
      setIsResetting(false); // Go back to login
      setInputPassword('');  // Clear old password field
    } catch (err) {
      let errorMsg = "Invalid Token or Password error.";
      if (err.response && err.response.data && err.response.data.password) {
          errorMsg = err.response.data.password[0];
      }
      setMessage({ text: errorMsg, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // --- LOGOUT ---
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setToken(null);
    setUsername('');
    setSubscription(null);
    setPayments([]);
  };

  // --- FETCH USER DATA ---
  const fetchData = (authToken) => {
    // 1. Get Subscription Status
    axios.get(`${API_URL}/api/billing/subscriptions/`, { 
      headers: { Authorization: `Bearer ${authToken}` } 
    })
    .then(res => { if (res.data.length > 0) setSubscription(res.data[0]); })
    .catch(err => { if (err.response?.status === 401) handleLogout(); });

    // 2. Get Payment History
    axios.get(`${API_URL}/api/billing/payments/`, { 
      headers: { Authorization: `Bearer ${authToken}` } 
    })
    .then(res => setPayments(res.data))
    .catch(console.error);
  };

  // --- MAKE PAYMENT ---
  const handlePayment = async () => {
    if (!subscription || !mpesaPhone) return;
    setIsLoading(true);
    setMessage({ text: 'Sending STK Push to your phone...', type: 'warning' });

    try {
      await axios.post(`${API_URL}/api/mpesa/pay/`, {
        phone: mpesaPhone,
        amount: subscription.price // Uses the price of their current plan
      }, { headers: { Authorization: `Bearer ${token}` } });
      setMessage({ text: 'Request sent! Check your phone to complete payment.', type: 'success' });
    } catch (err) {
      setMessage({ text: 'Payment Failed. Ensure phone format is 2547...', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // ==========================================
  // 4. RENDER: AUTH SCREENS
  // ==========================================
  
  if (!token) {
    return (
      <div className="login-container">
        <div className="login-card">
          <h2>
            {isRegistering ? 'Create Account' : 
             isResetting === 'confirm' ? 'Set New Password' :
             isResetting ? 'Reset Password' : 'ISP Customer Portal'}
          </h2>
          
          {/* --- A. LOGIN FORM --- */}
          {!isRegistering && !isResetting && (
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
              
              <div style={{marginTop: '15px', textAlign: 'center', fontSize: '0.9rem'}}>
                <p>New user? <span style={{color: '#2563eb', cursor: 'pointer', fontWeight: 'bold'}} onClick={() => {setIsRegistering(true); setMessage({text:'', type:''})}}>Create an account</span></p>
                <p style={{marginTop: '5px'}}><span style={{color: '#666', cursor: 'pointer'}} onClick={() => {setIsResetting(true); setMessage({text:'', type:''})}}>Forgot Password?</span></p>
              </div>
            </form>
          )}

          {/* --- B. REGISTER FORM --- */}
          {isRegistering && (
            <form onSubmit={handleRegister}>
              <div>
                <label>Username</label>
                <input type="text" onChange={e => setRegUsername(e.target.value)} required />
              </div>
              <div>
                <label>Email (Required for receipts)</label>
                <input type="email" onChange={e => setRegEmail(e.target.value)} required />
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

          {/* --- C. FORGOT PASSWORD (STEP 1) --- */}
          {isResetting === true && (
            <form onSubmit={handleRequestReset}>
              <p style={{fontSize: '0.9rem', color: '#666', marginBottom: '15px'}}>Enter your email address and we will send you a reset token.</p>
              <div>
                <label>Email Address</label>
                <input type="email" onChange={e => setResetEmail(e.target.value)} required />
              </div>
              {message.text && <p className={`msg-${message.type}`} style={{color: message.type==='error'?'red':'green', textAlign:'center'}}>{message.text}</p>}
              
              <button type="submit" className="btn-primary" disabled={isLoading}>{isLoading ? 'Sending...' : 'Send Reset Token'}</button>
              <p style={{marginTop:'15px', textAlign:'center', cursor:'pointer', color:'#2563eb'}} onClick={() => setIsResetting(false)}>Back to Login</p>
            </form>
          )}

          {/* --- D. FORGOT PASSWORD (STEP 2) --- */}
          {isResetting === 'confirm' && (
            <form onSubmit={handleConfirmReset}>
               <p style={{fontSize: '0.9rem', color: '#666', marginBottom: '15px'}}>Check your email for the token.</p>
              <div>
                <label>Reset Token</label>
                <input type="text" placeholder="e.g. 8f3a..." onChange={e => setResetToken(e.target.value)} required />
              </div>
              <div>
                <label>New Password</label>
                <input type="password" onChange={e => setNewPassword(e.target.value)} required />
              </div>
              {message.text && <p className={`msg-${message.type}`} style={{color: message.type==='error'?'red':'green', textAlign:'center'}}>{message.text}</p>}
              
              <button type="submit" className="btn-primary" disabled={isLoading}>{isLoading ? 'Updating...' : 'Set New Password'}</button>
            </form>
          )}

        </div>
      </div>
    );
  }

  // ==========================================
  // 5. RENDER: MAIN DASHBOARD
  // ==========================================
  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand-logo"><span>📡 WiFi Portal</span></div>
        <nav className="nav-links">
          <div className={`nav-item ${activeView === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveView('dashboard')}>📊 My Dashboard</div>
          <div className={`nav-item ${activeView === 'history' ? 'active' : ''}`} onClick={() => setActiveView('history')}>💳 Payment History</div>
        </nav>
        <div className="logout-btn" onClick={handleLogout}>Sign Out</div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="header">
          <h1>{activeView === 'dashboard' ? 'Overview' : 'Transaction History'}</h1>
          <div className="user-info">Logged in as <strong>{username}</strong></div>
        </header>

        {/* Dashboard View */}
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

        {/* History View */}
        {activeView === 'history' && (
          <div className="table-container">
            <table>
              <thead><tr><th>Date</th><th>Receipt</th><th>Amount</th><th>Status</th></tr></thead>
              <tbody>
                {payments.map((pay) => (
                  <tr key={pay.id}>
                    <td>{new Date(pay.created_at).toLocaleDateString()}</td>
                    <td>{pay.transaction_id || pay.mpesa_receipt_number || '---'}</td>
                    <td>KES {pay.amount}</td>
                    <td>
                        <span style={{
                            padding: '4px 8px', 
                            borderRadius: '4px', 
                            backgroundColor: pay.status === 'Completed' ? '#dcfce7' : '#fee2e2',
                            color: pay.status === 'Completed' ? '#166534' : '#991b1b'
                        }}>
                        {pay.status}
                        </span>
                    </td>
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