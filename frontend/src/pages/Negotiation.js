import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function Negotiation() {
  const [negotiations, setNegotiations] = useState([]);
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selectedLetter, setSelectedLetter] = useState(null);
  const [form, setForm] = useState({
    loan_id: '', lender_name: '', negotiation_type: 'settlement',
    proposed_settlement_amount: '', notes: '',
  });
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [negRes, loanRes] = await Promise.all([
        api.get('/api/negotiations/'),
        api.get('/api/loans/'),
      ]);
      setNegotiations(negRes.data);
      setLoans(loanRes.data);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setGenerating(true);

    const selectedLoan = loans.find(l => l.id === parseInt(form.loan_id));
    if (!selectedLoan) { setError('Please select a loan'); setGenerating(false); return; }

    try {
      const payload = {
        loan_id: parseInt(form.loan_id),
        lender_name: form.lender_name || selectedLoan.lender_name,
        negotiation_type: form.negotiation_type,
        proposed_settlement_amount: form.proposed_settlement_amount ? parseFloat(form.proposed_settlement_amount) : null,
        notes: form.notes || null,
      };
      const res = await api.post('/api/negotiations/', payload);
      setSelectedLetter(res.data.ai_generated_letter);
      setShowForm(false);
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate negotiation letter');
    }
    setGenerating(false);
  };

  const updateStatus = async (id, status) => {
    try {
      await api.put(`/api/negotiations/${id}/status`, { status });
      fetchData();
    } catch (err) { console.error(err); }
  };

  if (loading) return <div className="loader" style={{ marginTop: 100 }}></div>;

  const STATUS_BADGES = {
    DRAFT: 'badge-warning', SENT: 'badge-info', ACCEPTED: 'badge-success', REJECTED: 'badge-danger',
  };

  return (
    <div>
      <div className="topbar">
        <h2>Negotiation Letters</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>+ Generate Letter</button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {/* AI Generated Letter Modal */}
      {selectedLetter && (
        <div className="modal-overlay" onClick={() => setSelectedLetter(null)}>
          <div className="modal" style={{ maxWidth: 700 }} onClick={(e) => e.stopPropagation()}>
            <h3>AI-Generated Negotiation Letter</h3>
            <div style={{ whiteSpace: 'pre-wrap', padding: 16, background: '#f9fafb', borderRadius: 8, border: '1px solid #e5e7eb', maxHeight: 400, overflowY: 'auto', fontFamily: 'monospace', fontSize: '0.9rem', lineHeight: 1.8 }}>
              {selectedLetter}
            </div>
            <div style={{ marginTop: 16, display: 'flex', gap: 12 }}>
              <button className="btn btn-primary" onClick={() => { navigator.clipboard.writeText(selectedLetter); alert('Copied to clipboard!'); }}>Copy</button>
              <button className="btn btn-outline" onClick={() => setSelectedLetter(null)}>Close</button>
            </div>
          </div>
        </div>
      )}

      {/* Generate Form */}
      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Generate Negotiation Letter</h3>
            {generating && <p style={{ color: '#2563eb', marginBottom: 12 }}>AI is generating your letter...</p>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Select Loan *</label>
                <select className="form-control" value={form.loan_id} onChange={(e) => setForm({ ...form, loan_id: e.target.value })} required>
                  <option value="">-- Choose a loan --</option>
                  {loans.map(l => <option key={l.id} value={l.id}>{l.lender_name} - ₹{l.outstanding_amount.toLocaleString('en-IN')}</option>)}
                </select>
              </div>
              <div className="grid grid-2">
                <div className="form-group">
                  <label>Negotiation Type *</label>
                  <select className="form-control" value={form.negotiation_type} onChange={(e) => setForm({ ...form, negotiation_type: e.target.value })}>
                    <option value="settlement">Settlement</option>
                    <option value="restructuring">Restructuring</option>
                    <option value="waiver">Interest Waiver</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Proposed Settlement Amount (INR)</label>
                  <input type="number" className="form-control" value={form.proposed_settlement_amount} onChange={(e) => setForm({ ...form, proposed_settlement_amount: e.target.value })} placeholder="Leave empty for AI suggestion" />
                </div>
              </div>
              <div className="form-group">
                <label>Notes</label>
                <textarea className="form-control" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} rows={3} />
              </div>
              <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
                <button type="submit" className="btn btn-primary" disabled={generating}>
                  {generating ? 'Generating...' : 'Generate Letter'}
                </button>
                <button type="button" className="btn btn-outline" onClick={() => setShowForm(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Negotiations List */}
      {negotiations.length === 0 ? (
        <div className="card"><div className="empty-state"><p>No negotiations yet. Generate your first AI-powered letter.</p></div></div>
      ) : (
        <div className="grid grid-2">
          {negotiations.map((neg) => (
            <div className="card" key={neg.id}>
              <div className="card-header">
                <h3>{neg.lender_name}</h3>
                <span className={`badge ${STATUS_BADGES[neg.status]}`}>{neg.status}</span>
              </div>
              <p style={{ fontSize: '0.9rem', color: '#6b7280', marginBottom: 8 }}>Type: <strong>{neg.negotiation_type}</strong></p>
              {neg.proposed_settlement_amount && (
                <p style={{ fontSize: '0.9rem', marginBottom: 4 }}>Proposed: ₹{neg.proposed_settlement_amount.toLocaleString('en-IN')} ({neg.settlement_percentage}%)</p>
              )}
              {neg.ai_generated_letter && (
                <button className="btn btn-outline btn-sm" style={{ marginTop: 8 }} onClick={() => setSelectedLetter(neg.ai_generated_letter)}>View Letter</button>
              )}
              <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {neg.status !== 'SENT' && <button className="btn btn-primary btn-sm" onClick={() => updateStatus(neg.id, 'SENT')}>Mark Sent</button>}
                {neg.status === 'SENT' && <button className="btn btn-success btn-sm" onClick={() => updateStatus(neg.id, 'ACCEPTED')}>Accepted</button>}
                {neg.status === 'SENT' && <button className="btn btn-danger btn-sm" onClick={() => updateStatus(neg.id, 'REJECTED')}>Rejected</button>}
              </div>
              <p style={{ fontSize: '0.8rem', color: '#9ca3af', marginTop: 12 }}>Created: {new Date(neg.created_at).toLocaleDateString()}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
