import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; 
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Environment Helper (Connects to your Django/Render Backend)
const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

function App() {
  // ==========================================
  // 1. STATE MANAGEMENT
  // ==========================================
  
  // Auth State
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [username, setUsername] = useState(localStorage.getItem('username') || '');

  // UI State
  const [activeView, setActiveView] = useState('dashboard'); // 'dashboard', 'plans', 'history', or 'support'
  const [isRegistering, setIsRegistering] = useState(false); 
  const [isResetting, setIsResetting] = useState(false);     
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  // Data State
  const [subscription, setSubscription] = useState(null);
  const [payments, setPayments] = useState([]);
  const [liveUsage, setLiveUsage] = useState({ upload_mb: 0, download_mb: 0 });
  const [usageData, setUsageData] = useState([]);
  const [availablePackages, setAvailablePackages] = useState([]); 
  
  // SUPPORT TICKET STATE
  const [tickets, setTickets] = useState([]);
  const [ticketSubject, setTicketSubject] = useState('');
  const [ticketCategory, setTicketCategory] = useState('INTERNET');
  const [ticketDescription, setTicketDescription] = useState('');

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
      fetchPackages(token); // Fetch available plans on login
      // Poll live usage every 30 seconds
      const usageInterval = setInterval(() => fetchLiveUsage(token), 30000);
      return () => clearInterval(usageInterval);
    }
  }, [token]);
  
  // Effect for Auto-Polling Tickets
  useEffect(() => {
    let ticketInterval = null;
    if (token && activeView === 'support') {
      ticketInterval = setInterval(() => {
        refreshTickets(token);
      }, 60000);
    }
    return () => {
      if (ticketInterval) clearInterval(ticketInterval);
    };
  }, [token, activeView]);

  // ==========================================
  // 3. API ACTIONS & DATA FETCHING
  // ==========================================

  const fetchLiveUsage = (authToken) => {
      axios.get(`${API_URL}/api/billing/usage/current/`, { headers: { Authorization: `Bearer ${authToken}` } })
      .then(res => setLiveUsage(res.data))
      .catch(console.error);
  }
  
  // Fetch all available WiFi packages/plans
  const fetchPackages = (authToken) => {
      axios.get(`${API_URL}/api/plans/wifipackages/`, { headers: { Authorization: `Bearer ${authToken}` } })
      .then(res => setAvailablePackages(res.data))
      .catch(console.error);
  }

  // --- FETCH ALL USER DATA ---
  const fetchData = (authToken) => {
    const config = { headers: { Authorization: `Bearer ${authToken}` } };

    // 1. Subscription
    axios.get(`${API_URL}/api/billing/subscriptions/`, config)
      .then(res => { 
        if (res.data.length > 0) setSubscription(res.data[0]); 
        else setSubscription(null); 
      })
      .catch(err => { if (err.response?.status === 401) handleLogout(); });

    // 2. Payments
    axios.get(`${API_URL}/api/billing/payments/`, config)
      .then(res => setPayments(res.data))
      .catch(console.error);

    // 3. Live Usage (Current Session)
    fetchLiveUsage(authToken);

    // 4. Historical Usage (Graph)
    axios.get(`${API_URL}/api/billing/usage/history/`, config)
      .then(res => {
        if (res.data.length === 0) {
           setUsageData([]);
        } else {
           setUsageData(res.data);
        }
      })
      .catch(console.error);

    // 5. Support Tickets
    refreshTickets(authToken);
  };
  
  // --- REFRESH TICKETS ---
  const refreshTickets = (authToken, showMessage = false) => {
    const config = { headers: { Authorization: `Bearer ${authToken}` } };
    axios.get(`${API_URL}/api/support/tickets/`, config)
      .then(res => {
        setTickets(res.data);
        if (showMessage) setMessage({ text: 'Tickets refreshed.', type: 'info' });
      })
      .catch(console.error);
  };
  
  // --- HANDLE PLAN CHANGE (Upgrade/Downgrade) ---
  const handlePlanChange = async (newPackageId) => {
    setIsLoading(true);
    setMessage({ text: 'Processing plan change...', type: 'warning' });
    
    try {
      const res = await axios.post(`${API_URL}/api/billing/plan-actions/change_plan/`, 
        { package_id: newPackageId }, 
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setMessage({ text: res.data.detail, type: 'success' });
      fetchData(token); // Refresh subscription data
      setActiveView('dashboard'); // Go to dashboard to see changes
      
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to change plan.';
      setMessage({ text: detail, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // --- HANDLE RENEWAL ---
  const handleRenew = async () => {
    if (!subscription) {
      setMessage({ text: 'Cannot renew: No active subscription found.', type: 'error' });
      return;
    }
    
    setIsLoading(true);
    setMessage({ text: 'Processing renewal...', type: 'warning' });
    
    try {
      const res = await axios.post(`${API_URL}/api/billing/plan-actions/renew/`, 
        {}, 
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setMessage({ text: res.data.detail, type: 'success' });
      fetchData(token); // Refresh subscription data

    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to renew subscription.';
      setMessage({ text: detail, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };


  // --- LOGIN ---
  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ text: '', type: '' });
    try {
      const res = await axios.post(`${API_URL}/api/auth/login/`, { username: inputUsername, password: inputPassword });
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
      await axios.post(`${API_URL}/api/auth/register/`, {
        username: regUsername, 
        password: regPassword, 
        email: regEmail, 
        phone_number: regPhone
      });
      setMessage({ text: 'Account created! Please log in.', type: 'success' });
      setIsRegistering(false); 
      setInputUsername(regUsername);
    } catch (err) {
      let errorMsg = "Registration failed.";
      
      if (err.response && err.response.data) {
        const errors = err.response.data;
        if (errors.username) errorMsg = `Username: ${errors.username[0]}`;
        else if (errors.password) errorMsg = `Password: ${errors.password[0]}`;
        else if (errors.phone_number) errorMsg = `Phone: ${errors.phone_number[0]}`;
        else if (errors.email) errorMsg = `Email: ${errors.email[0]}`;
        else errorMsg = "Registration failed. Check format of all fields.";
      }
      
      setMessage({ text: errorMsg, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // --- PASSWORD RESET (Request) ---
  const handleRequestReset = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ text: 'Sending email...', type: 'warning' });
    try {
      await axios.post(`${API_URL}/api/auth/password_reset/`, { email: resetEmail });
      setMessage({ text: 'Check your email for the reset token!', type: 'success' });
      setIsResetting('confirm'); 
    } catch (err) {
      let errorMsg = "Email not found or server error.";
      if (err.response?.data?.email) errorMsg = err.response.data.email[0];
      setMessage({ text: errorMsg, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // --- PASSWORD RESET (Confirm) ---
  const handleConfirmReset = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await axios.post(`${API_URL}/api/auth/password_reset/confirm/`, { token: resetToken, password: newPassword });
      setMessage({ text: 'Password changed successfully! Please login.', type: 'success' });
      setIsResetting(false); 
      setInputPassword('');  
    } catch (err) {
      setMessage({ text: "Invalid Token or Password error.", type: 'error' });
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

  // --- MAKE PAYMENT (M-Pesa) ---
  const handlePayment = async () => {
    if (!subscription || !mpesaPhone) return;
    setIsLoading(true);
    setMessage({ text: 'Sending STK Push to your phone...', type: 'warning' });

    try {
      await axios.post(`${API_URL}/api/mpesa/pay/`, {
        phone: mpesaPhone,
        amount: subscription.price 
      }, { headers: { Authorization: `Bearer ${token}` } });
      setMessage({ text: 'Request sent! Check your phone.', type: 'success' });
    } catch (err) {
      setMessage({ text: 'Payment Failed. Check phone number or server configuration.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // --- SUBMIT TICKET ---
  const handleTicketSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ text: '', type: '' });
    try {
      await axios.post(`${API_URL}/api/support/tickets/`, {
        subject: ticketSubject,
        category: ticketCategory,
        description: ticketDescription
      }, { headers: { Authorization: `Bearer ${token}` } });
      
      setMessage({ text: 'Ticket submitted! We will contact you shortly.', type: 'success' });
      setTicketSubject('');
      setTicketDescription('');
      refreshTickets(token); // Refresh list
    } catch (err) {
      setMessage({ text: 'Failed to submit ticket.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // ==========================================
  // 4. RENDER: AUTH SCREENS (Login/Register/Reset)
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
          
          {/* --- LOGIN FORM --- */}
          {!isRegistering && !isResetting && (
            <form onSubmit={handleLogin}>
              <div><label>Username</label><input type="text" onChange={e => setInputUsername(e.target.value)} value={inputUsername} required /></div>
              <div><label>Password</label><input type="password" onChange={e => setInputPassword(e.target.value)} value={inputPassword} required /></div>
              
              {message.text && <p className={`msg-${message.type}`} style={{color: message.type==='error'?'red':'green', textAlign:'center'}}>{message.text}</p>}
              
              <button type="submit" className="btn-primary" disabled={isLoading}>{isLoading ? 'Logging in...' : 'Login'}</button>
              
              <div style={{marginTop: '15px', textAlign: 'center', fontSize: '0.9rem'}}>
                <p>New here? <span style={{color: '#2563eb', cursor: 'pointer', fontWeight: 'bold'}} onClick={() => {setIsRegistering(true); setMessage({text:'', type:''})}}>Create Account</span></p>
                <p style={{marginTop: '5px'}}><span style={{color: '#666', cursor: 'pointer'}} onClick={() => {setIsResetting(true); setMessage({text:'', type:''})}}>Forgot Password?</span></p>
              </div>
            </form>
          )}

          {/* --- REGISTER FORM --- */}
          {isRegistering && (
            <form onSubmit={handleRegister}>
              <div><label>Username</label><input type="text" onChange={e => setRegUsername(e.target.value)} required /></div>
              <div><label>Email</label><input type="email" onChange={e => setRegEmail(e.target.value)} required /></div>
              <div><label>Phone</label><input type="text" placeholder="2547XXXXXXXX" onChange={e => setRegPhone(e.target.value)} required /></div>
              <div><label>Password</label><input type="password" onChange={e => setRegPassword(e.target.value)} required /></div>
              {message.text && <p className={`msg-${message.type}`} style={{color: message.type==='error'?'red':'green', textAlign:'center'}}>{message.text}</p>}
              <button type="submit" className="btn-primary" disabled={isLoading}>{isLoading ? 'Creating...' : 'Sign Up'}</button>
              <p style={{marginTop: '15px', textAlign: 'center', fontSize: '0.9rem'}}><span style={{color: '#2563eb', cursor: 'pointer', fontWeight: 'bold'}} onClick={() => {setIsRegistering(false); setMessage({text:'', type:''})}}>Back to Login</span></p>
            </form>
          )}

          {/* --- FORGOT PASSWORD --- */}
          {isResetting === true && (
            <form onSubmit={handleRequestReset}>
              <p style={{fontSize: '0.9rem', color: '#666'}}>Enter your email for a reset token.</p>
              <div><label>Email</label><input type="email" onChange={e => setResetEmail(e.target.value)} required /></div>
              {message.text && <p className={`msg-${message.type}`} style={{color: message.type==='error'?'red':'green', textAlign:'center'}}>{message.text}</p>}
              <button type="submit" className="btn-primary" disabled={isLoading}>{isLoading ? 'Sending...' : 'Send Token'}</button>
              <p style={{marginTop:'15px', textAlign:'center', cursor:'pointer', color:'#2563eb'}} onClick={() => setIsResetting(false)}>Cancel</p>
            </form>
          )}

          {/* --- CONFIRM PASSWORD --- */}
          {isResetting === 'confirm' && (
            <form onSubmit={handleConfirmReset}>
              <div><label>Token</label><input type="text" onChange={e => setResetToken(e.target.value)} required /></div>
              <div><label>New Password</label><input type="password" onChange={e => setNewPassword(e.target.value)} required /></div>
              {message.text && <p className={`msg-${message.type}`} style={{color: message.type==='error'?'red':'green', textAlign:'center'}}>{message.text}</p>}
              <button type="submit" className="btn-primary" disabled={isLoading}>{isLoading ? 'Updating...' : 'Set Password'}</button>
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
          <div className={`nav-item ${activeView === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveView('dashboard')}>📊 Dashboard</div>
          <div className={`nav-item ${activeView === 'plans' ? 'active' : ''}`} onClick={() => setActiveView('plans')}>📦 Plans & Renew</div>
          <div className={`nav-item ${activeView === 'history' ? 'active' : ''}`} onClick={() => setActiveView('history')}>💳 Payments</div>
          <div className={`nav-item ${activeView === 'support' ? 'active' : ''}`} onClick={() => setActiveView('support')}>🎫 Help Desk</div>
        </nav>
        <div className="logout-btn" onClick={handleLogout}>Sign Out</div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="header">
          <h1>
            {activeView === 'dashboard' ? 'Overview' : 
             activeView === 'plans' ? 'Plan Management' : 
             activeView === 'history' ? 'Transaction History' : 
             'Help Desk'}
          </h1>
          <div className="user-info">User: <strong>{username}</strong></div>
        </header>

        {/* --- GLOBAL MESSAGE DISPLAY --- */}
        {message.text && (
            <div className={`global-msg msg-${message.type}`} style={{padding: '10px', marginBottom:'20px', borderRadius: '6px', backgroundColor: message.type === 'success' ? '#d1fae5' : message.type === 'error' ? '#fee2e2' : '#fff7ed', color: message.type === 'success' ? '#065f46' : message.type === 'error' ? '#991b1b' : '#b45309', border: `1px solid ${message.type === 'success' ? '#34d399' : message.type === 'error' ? '#f87171' : '#fcd34d'}`}}>
                {message.text}
            </div>
        )}
        
        {/* --- DASHBOARD VIEW --- */}
        {activeView === 'dashboard' && (
          <>
            {/* 1. Status Cards */}
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Current Plan</h3>
                <div className="value">{subscription ? subscription.package_name : 'No Plan'}</div>
                <div style={{marginTop:'10px', color: subscription?.is_active ? 'green' : 'red'}}>
                  {subscription?.is_active ? '● Online' : '● Inactive'}
                </div>
              </div>
              <div className="stat-card">
                <h3>Current Session (Live)</h3>
                <div style={{display:'flex', justifyContent:'space-between', marginTop:'10px'}}>
                  <div style={{textAlign:'center'}}>
                    <span style={{fontSize:'1.5rem', color:'#2563eb'}}>⬇</span>
                    <div style={{fontWeight:'bold'}}>{liveUsage.download_mb} MB</div>
                  </div>
                  <div style={{textAlign:'center'}}>
                     <span style={{fontSize:'1.5rem', color:'#16a34a'}}>⬆</span>
                     <div style={{fontWeight:'bold'}}>{liveUsage.upload_mb} MB</div>
                  </div>
                </div>
              </div>
              <div className="stat-card">
                <h3>Next Renewal</h3>
                <div className="value">{subscription ? new Date(subscription.end_date).toDateString() : '--'}</div>
              </div>
            </div>

            {/* 2. Usage Graph (Recharts) */}
            <div className="table-container" style={{marginBottom: '20px'}}>
               <div className="table-header"><h3>Data Usage History (Last 7 Days)</h3></div>
               <div style={{ width: '100%', height: 300, padding: '20px' }}>
                 <ResponsiveContainer>
                   <LineChart data={usageData}>
                     <CartesianGrid strokeDasharray="3 3" />
                     <XAxis dataKey="date" />
                     <YAxis />
                     <Tooltip />
                     <Line type="monotone" dataKey="download" stroke="#2563eb" strokeWidth={3} name="Download (MB)" />
                     <Line type="monotone" dataKey="upload" stroke="#16a34a" strokeWidth={3} name="Upload (MB)" />
                   </LineChart>
                 </ResponsiveContainer>
               </div>
            </div>

            {/* 3. Top Up Section */}
            <div className="table-container">
              <div className="table-header"><h3>Quick Top-Up (M-Pesa)</h3></div>
              <div style={{padding: '2rem', maxWidth: '500px'}}>
                <p style={{marginBottom: '1rem', color: '#6b7280'}}>Enter M-Pesa number to renew your current plan.</p>
                <input type="text" placeholder="2547XXXXXXXX" value={mpesaPhone} onChange={e => setMpesaPhone(e.target.value)}/>
                <button className="btn-primary" onClick={handlePayment} disabled={isLoading || !subscription} style={{marginTop:'10px'}}>
                  {isLoading ? 'Processing...' : `Pay KES ${subscription ? subscription.price : '0'} Now`}
                </button>
                <button className="btn-secondary" onClick={handleRenew} disabled={isLoading || !subscription} style={{marginTop:'10px', marginLeft: '10px'}}>
                   {isLoading ? 'Renewing...' : `Renew Subscription`}
                </button>
                <p style={{marginTop: '15px', fontSize: '0.85rem', color: '#2563eb', cursor: 'pointer'}} onClick={() => setActiveView('plans')}>
                   View available plans to upgrade or downgrade »
                </p>
              </div>
            </div>
          </>
        )}

        {/* --- PLANS VIEW --- */}
        {activeView === 'plans' && (
            <div className="table-container">
                <div className="table-header">
                    <h3>All Available Internet Plans</h3>
                    {subscription && <p style={{color: '#16a34a'}}>Your Current Plan: <strong>{subscription.package_name}</strong> (Expires: {new Date(subscription.end_date).toLocaleDateString()})</p>}
                </div>
                
                {availablePackages.length > 0 ? (
                    <div className="plans-grid">
                        {availablePackages.map(pkg => (
                            <div key={pkg.id} className={`plan-card ${subscription && subscription.package_name === pkg.name ? 'current-plan' : ''}`}>
                                <h4>{pkg.name}</h4>
                                <p className="plan-speed">{pkg.max_download_speed} Mbps / {pkg.max_upload_speed} Mbps</p>
                                <p className="plan-price">KES {pkg.price} / {pkg.duration_days} Days</p>
                                <p className="plan-data">Data Cap: {pkg.data_cap_mb === 0 ? 'Unlimited' : `${(pkg.data_cap_mb / 1024).toFixed(0)} GB`}</p>
                                
                                {subscription && subscription.package_name === pkg.name ? (
                                    <button className="btn-current" disabled>Current Plan</button>
                                ) : (
                                    <button 
                                        className="btn-primary" 
                                        onClick={() => handlePlanChange(pkg.id)}
                                        disabled={isLoading}
                                    >
                                        {isLoading ? 'Processing...' : (
                                            subscription && subscription.package.price < pkg.price ? 'Upgrade Now' : 'Downgrade Now'
                                        )}
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                ) : (
                    // Display message if no packages are loaded
                    <p style={{textAlign: 'center', padding: '50px', color: '#dc2626'}}>
                        ⚠️ Error: Could not load packages or no packages have been created by the Admin yet.
                    </p>
                )}
            </div>
        )}

        {/* --- HISTORY VIEW --- */}
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
                      <span style={{padding: '4px 8px', borderRadius: '4px', backgroundColor: pay.status === 'Completed' ? '#dcfce7' : '#fee2e2', color: pay.status === 'Completed' ? '#166534' : '#991b1b'}}>
                        {pay.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* --- SUPPORT VIEW --- */}
        {activeView === 'support' && (
          <div className="table-container">
            <div className="table-header" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                <h3>Open a New Ticket</h3>
                <button 
                    className="btn-primary" 
                    onClick={() => refreshTickets(token, true)} 
                    disabled={isLoading} 
                    style={{padding: '8px 15px', fontSize: '0.9rem', backgroundColor: '#6b7280'}}
                >
                    Refresh List
                </button>
            </div>
            
            <div style={{padding: '20px'}}>
              <form onSubmit={handleTicketSubmit}>
                <div style={{marginBottom: '15px'}}>
                   <label style={{display:'block', marginBottom:'5px', fontWeight:'bold'}}>Category</label>
                   <select style={{width:'100%', padding:'8px'}} value={ticketCategory} onChange={e => setTicketCategory(e.target.value)}>
                     <option value="INTERNET">No Internet / Slow Speed</option>
                     <option value="BILLING">Billing Issue</option>
                     <option value="RELOCATION">Relocation Request</option>
                     <option value="OTHER">Other</option>
                   </select>
                </div>
                <div style={{marginBottom: '15px'}}>
                   <label style={{display:'block', marginBottom:'5px', fontWeight:'bold'}}>Subject</label>
                   <input type="text" style={{width:'100%', padding:'8px'}} placeholder="e.g. My internet is off" value={ticketSubject} onChange={e => setTicketSubject(e.target.value)} required />
                </div>
                <div style={{marginBottom: '15px'}}>
                   <label style={{display:'block', marginBottom:'5px', fontWeight:'bold'}}>Description</label>
                   <textarea style={{width:'100%', padding:'8px', height:'100px'}} placeholder="Describe the issue..." value={ticketDescription} onChange={e => setTicketDescription(e.target.value)} required></textarea>
                </div>
                <button className="btn-primary" disabled={isLoading}>{isLoading ? 'Submitting...' : 'Submit Ticket'}</button>
              </form>
            </div>

            <div className="table-header" style={{marginTop: '30px'}}><h3>My Recent Tickets</h3></div>
            <table>
              <thead>
                <tr><th>Date</th><th>Subject</th><th>Status</th><th>Status Log</th></tr> 
              </thead>
              <tbody>
                {tickets.length === 0 ? <tr><td colSpan="4" style={{textAlign:'center', padding:'20px'}}>No tickets found.</td></tr> : 
                 tickets.map((t) => (
                  <tr key={t.id}>
                    <td>{new Date(t.created_at).toLocaleDateString()}</td>
                    <td>
                      <strong>{t.subject}</strong><br/>
                      <span style={{fontSize:'0.8rem', color:'#666'}}>{t.category_display}</span>
                    </td>
                    <td>
                        <span style={{
                            padding: '4px 8px', borderRadius: '4px', fontSize:'0.85rem',
                            backgroundColor: t.status === 'OPEN' ? '#fff7ed' : t.status === 'RESOLVED' ? '#dcfce7' : '#f3f4f6',
                            color: t.status === 'OPEN' ? '#c2410c' : t.status === 'RESOLVED' ? '#166534' : '#374151'
                        }}>
                        {t.status_display}
                        </span>
                    </td>
                    <td style={{maxWidth: '300px', fontSize: '0.85rem', color: '#4b5563'}}>
                      {/* DISPLAY THE HISTORY LOG (Ticket Updates) */}
                      {t.updates && t.updates
                        .filter(u => u.is_public) // Show only public updates
                        .map((update, index) => (
                          <div key={index} style={{borderLeft: '2px solid #3b82f6', paddingLeft: '8px', marginBottom: '5px'}}>
                            <div style={{color: '#3b82f6', fontWeight: 'bold'}}>
                              {update.updated_by_username || 'Admin'} - {new Date(update.created_at).toLocaleDateString()}
                            </div>
                            {update.note}
                          </div>
                        ))
                      }
                      {/* Show final resolution below the log */}
                      {t.admin_response && <div style={{marginTop: '10px', color: '#16a34a', fontWeight:'bold'}}>Final Resolution: {t.admin_response}</div>}
                      
                      {!(t.updates && t.updates.filter(u => u.is_public).length) && !t.admin_response && (
                        <em style={{color:'#9ca3af'}}>Waiting for first progress update...</em>
                      )}
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