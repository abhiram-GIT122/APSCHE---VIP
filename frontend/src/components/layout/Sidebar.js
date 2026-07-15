import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const links = [
    { to: '/dashboard', label: 'Dashboard', icon: '📊' },
    { to: '/loans', label: 'My Loans', icon: '💳' },
    { to: '/negotiation', label: 'Negotiations', icon: '✉️' },
    { to: '/settlements', label: 'Settlements', icon: '🤝' },
    { to: '/profile', label: 'Profile', icon: '👤' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h1>Fin<span>Relief</span> AI</h1>
        <p>AI-Powered Debt Recovery</p>
      </div>
      <nav>
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          >
            <span>{link.icon}</span>
            {link.label}
          </NavLink>
        ))}
      </nav>
      <div style={{ marginTop: 'auto', padding: '16px 24px', borderTop: '1px solid #374151', position: 'absolute', bottom: 0, width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
          <div className="user-avatar" style={{ width: 32, height: 32, fontSize: '0.85rem' }}>
            {(user?.full_name || user?.username || 'U').charAt(0).toUpperCase()}
          </div>
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 500 }}>{user?.username || 'User'}</div>
            <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>{user?.email}</div>
          </div>
        </div>
        <button className="btn btn-outline" style={{ width: '100%', justifyContent: 'center', borderColor: '#4b5563', color: '#d1d5db' }} onClick={handleLogout}>
          Logout
        </button>
      </div>
    </aside>
  );
}
