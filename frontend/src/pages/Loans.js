import React, { useState, useEffect } from 'react';
import api from '../services/api';

const LOAN_TYPES = ['personal', 'home', 'education', 'credit_card', 'vehicle', 'business'];

export default function Loans() {
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editLoan, setEditLoan] = useState(null);
  const [form, setForm] = useState({
    lender_name: '', loan_type: 'personal', outstanding_amount: '', monthly_emi: '',
    interest_rate: '', overdue_duration_months: 0, tenure_months: '', original_amount: '',
  });
  const [error, setError] = useState('');

  useEffect(() => { fetchLoans(); }, []);

  const fetchLoans = async () => {
    try {
      const res = await api.get('/api/loans/');
      setLoans(res.data);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const payload = {
        ...form,
        outstanding_amount: parseFloat(form.outstanding_amount),
        monthly_emi: parseFloat(form.monthly_emi),
        interest_rate: form.interest_rate ? parseFloat(form.interest_rate) : null,
        overdue_duration_months: parseInt(form.overdue_duration_months) || 0,
        tenure_months: form.tenure_months ? parseInt(form.tenure_months) : null,
        original_amount: form.original_amount ? parseFloat(form.original_amount) : null,
      };

      if (editLoan) {
        await api.put(`/api/loans/${editLoan.id}`, {
          lender_name: payload.lender_name,
          outstanding_amount: payload.outstanding_amount,
          monthly_emi: payload.monthly_emi,
          overdue_duration_months: payload.overdue_duration_months,
        });
      } else {
        await api.post('/api/loans/', payload);
      }

      setShowForm(false);
      setEditLoan(null);
      resetForm();
      fetchLoans();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save loan');
    }
  };

  const handleEdit = (loan) => {
    setEditLoan(loan);
    setForm({
      lender_name: loan.lender_name,
      loan_type: loan.loan_type,
      outstanding_amount: loan.outstanding_amount,
      monthly_emi: loan.monthly_emi,
      interest_rate: loan.interest_rate || '',
      overdue_duration_months: loan.overdue_duration_months,
      tenure_months: loan.tenure_months || '',
      original_amount: loan.original_amount || '',
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this loan?')) return;
    try {
      await api.delete(`/api/loans/${id}`);
      fetchLoans();
    } catch (err) { console.error(err); }
  };

  const resetForm = () => {
    setForm({
      lender_name: '', loan_type: 'personal', outstanding_amount: '', monthly_emi: '',
      interest_rate: '', overdue_duration_months: 0, tenure_months: '', original_amount: '',
    });
  };

  if (loading) return <div className="loader" style={{ marginTop: 100 }}></div>;

  return (
    <div>
      <div className="topbar">
        <h2>My Loans</h2>
        <button className="btn btn-primary" onClick={() => { setShowForm(true); resetForm(); setEditLoan(null); }}>
          + Add Loan
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Loan Form Modal */}
      {showForm && (
        <div className="modal-overlay" onClick={() => { setShowForm(false); setEditLoan(null); }}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>{editLoan ? 'Edit Loan' : 'Add New Loan'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="grid grid-2">
                <div className="form-group">
                  <label>Lender Name *</label>
                  <input type="text" className="form-control" value={form.lender_name} onChange={(e) => setForm({ ...form, lender_name: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>Loan Type *</label>
                  <select className="form-control" value={form.loan_type} onChange={(e) => setForm({ ...form, loan_type: e.target.value })}>
                    {LOAN_TYPES.map(t => <option key={t} value={t}>{t.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Outstanding Amount (INR) *</label>
                  <input type="number" className="form-control" value={form.outstanding_amount} onChange={(e) => setForm({ ...form, outstanding_amount: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>Monthly EMI (INR) *</label>
                  <input type="number" className="form-control" value={form.monthly_emi} onChange={(e) => setForm({ ...form, monthly_emi: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>Original Amount (INR)</label>
                  <input type="number" className="form-control" value={form.original_amount} onChange={(e) => setForm({ ...form, original_amount: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Interest Rate (% per year)</label>
                  <input type="number" step="0.01" className="form-control" value={form.interest_rate} onChange={(e) => setForm({ ...form, interest_rate: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Overdue Duration (months)</label>
                  <input type="number" className="form-control" value={form.overdue_duration_months} onChange={(e) => setForm({ ...form, overdue_duration_months: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Tenure (months)</label>
                  <input type="number" className="form-control" value={form.tenure_months} onChange={(e) => setForm({ ...form, tenure_months: e.target.value })} />
                </div>
              </div>
              <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
                <button type="submit" className="btn btn-primary">{editLoan ? 'Update' : 'Add'} Loan</button>
                <button type="button" className="btn btn-outline" onClick={() => { setShowForm(false); setEditLoan(null); }}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Loans Table */}
      {loans.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <p>No loans added yet. Click "Add Loan" to get started.</p>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Lender</th><th>Type</th><th>Outstanding</th><th>EMI</th><th>Interest</th><th>Overdue</th><th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {loans.map((loan) => (
                  <tr key={loan.id}>
                    <td><strong>{loan.lender_name}</strong></td>
                    <td><span className="badge badge-info">{loan.loan_type}</span></td>
                    <td>₹{loan.outstanding_amount.toLocaleString('en-IN')}</td>
                    <td>{loan.monthly_emi.toLocaleString('en-IN')}</td>
                    <td>{loan.interest_rate ? `${loan.interest_rate}%` : '-'}</td>
                    <td>
                      {loan.overdue_duration_months > 0 ? (
                        <span className="badge badge-danger">{loan.overdue_duration_months} mo</span>
                      ) : (
                        <span className="badge badge-success">Current</span>
                      )}
                    </td>
                    <td>
                      <button className="btn btn-outline btn-sm" style={{ marginRight: 8 }} onClick={() => handleEdit(loan)}>Edit</button>
                      <button className="btn btn-danger btn-sm" onClick={() => handleDelete(loan.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
