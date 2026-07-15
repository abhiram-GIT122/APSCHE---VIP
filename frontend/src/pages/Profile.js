import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function Profile() {
  const { user, updateProfile } = useAuth();
  const [form, setForm] = useState({
    full_name: user?.full_name || '',
    phone: user?.phone || '',
    monthly_income: user?.monthly_income || '',
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setSaving(true);
    try {
      await updateProfile({
        ...form,
        monthly_income: form.monthly_income ? parseInt(form.monthly_income) : null,
      });
      setMessage('Profile updated successfully!');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    }
    setSaving(false);
  };

  return (
    <div>
      <div className="topbar">
        <h2>My Profile</h2>
      </div>

      <div className="grid grid-2">
        {/* Profile Info Card */}
        <div className="card">
          <h3 style={{ marginBottom: 20 }}>Account Information</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24, padding: 16, background: '#f9fafb', borderRadius: 8 }}>
            <div className="user-avatar" style={{ width: 60, height: 60, fontSize: '1.5rem' }}>
              {(user?.full_name || user?.username || 'U').charAt(0).toUpperCase()}
            </div>
            <div>
              <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>{user?.username}</div>
              <div style={{ color: '#6b7280', fontSize: '0.9rem' }}>{user?.email}</div>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f3f4f6' }}>
              <span style={{ color: '#6b7280' }}>Account Created</span>
              <span style={{ fontWeight: 500 }}>{new Date(user?.created_at).toLocaleDateString()}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f3f4f6' }}>
              <span style={{ color: '#6b7280' }}>Status</span>
              <span className="badge badge-success">Active</span>
            </div>
          </div>
        </div>

        {/* Edit Profile Form */}
        <div className="card">
          <h3 style={{ marginBottom: 20 }}>Edit Profile</h3>
          {message && <div className="alert alert-success">{message}</div>}
          {error && <div className="alert alert-error">{error}</div>}
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Full Name</label>
              <input type="text" className="form-control" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Phone</label>
              <input type="text" className="form-control" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Monthly Income (INR)</label>
              <input type="number" className="form-control" value={form.monthly_income} onChange={(e) => setForm({ ...form, monthly_income: e.target.value })} />
            </div>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
