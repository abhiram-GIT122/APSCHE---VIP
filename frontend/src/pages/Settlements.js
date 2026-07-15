import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function Settlements() {
  const [settlements, setSettlements] = useState([]);
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLoanId, setSelectedLoanId] = useState('');
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [setRes, loanRes] = await Promise.all([
        api.get('/api/settlements/'),
        api.get('/api/loans/'),
      ]);
      setSettlements(setRes.data);
      setLoans(loanRes.data);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  const handleGenerate = async () => {
    if (!selectedLoanId) { setError('Please select a loan'); return; }
    setError('');
    setGenerating(true);
    try {
      await api.post('/api/settlements/', { loan_id: parseInt(selectedLoanId) });
      setSelectedLoanId('');
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate settlement');
    }
    setGenerating(false);
  };

  const handleAccept = async (id) => {
    try {
      await api.post(`/api/settlements/${id}/accept`);
      fetchData();
    } catch (err) { console.error(err); }
  };

  if (loading) return <div className="loader" style={{ marginTop: 100 }}></div>;

  return (
    <div>
      <div className="topbar">
        <h2>Settlement Recommendations</h2>
      </div>

      {/* Generate Section */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h3 style={{ marginBottom: 16 }}>Generate New Settlement Recommendation</h3>
        {error && <div className="alert alert-error">{error}</div>}
        <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end' }}>
          <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
            <label>Select Loan</label>
            <select className="form-control" value={selectedLoanId} onChange={(e) => setSelectedLoanId(e.target.value)}>
              <option value="">-- Choose a loan --</option>
              {loans.map(l => <option key={l.id} value={l.id}>{l.lender_name} - ₹{l.outstanding_amount.toLocaleString('en-IN')}</option>)}
            </select>
          </div>
          <button className="btn btn-primary" onClick={handleGenerate} disabled={generating || !selectedLoanId}>
            {generating ? 'Analyzing...' : 'Generate AI Settlement'}
          </button>
        </div>
      </div>

      {/* Settlements List */}
      {settlements.length === 0 ? (
        <div className="card"><div className="empty-state"><p>No settlement recommendations yet. Select a loan above to get started.</p></div></div>
      ) : (
        <div className="grid grid-2">
          {settlements.map((s) => {
            const loan = loans.find(l => l.id === s.loan_id);
            return (
              <div className="card" key={s.id} style={{ borderLeft: s.is_accepted === 1 ? '4px solid #16a34a' : '4px solid #2563eb' }}>
                <div className="card-header">
                  <h3>{loan?.lender_name || 'Unknown Loan'}</h3>
                  {s.is_accepted === 1 ? (
                    <span className="badge badge-success">Accepted</span>
                  ) : (
                    <span className="badge badge-warning">Pending</span>
                  )}
                </div>
                <div className="grid grid-3" style={{ gap: 12, marginBottom: 16 }}>
                  <div>
                    <div className="stat-label">Recommended</div>
                    <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>₹{s.recommended_settlement_amount.toLocaleString('en-IN')}</div>
                  </div>
                  <div>
                    <div className="stat-label">Savings</div>
                    <div style={{ fontWeight: 700, fontSize: '1.1rem', color: '#16a34a' }}>₹{s.savings_amount.toLocaleString('en-IN')}</div>
                  </div>
                  <div>
                    <div className="stat-label">Settlement %</div>
                    <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>{s.settlement_percentage}%</div>
                  </div>
                </div>
                {s.rationale && (
                  <p style={{ fontSize: '0.9rem', color: '#4b5563', marginBottom: 12, padding: 10, background: '#f9fafb', borderRadius: 6 }}>{s.rationale}</p>
                )}
                {s.risk_factors && s.risk_factors.length > 0 && (
                  <div style={{ marginBottom: 12 }}>
                    <strong style={{ fontSize: '0.85rem', color: '#dc2626' }}>Risk Factors:</strong>
                    <ul style={{ paddingLeft: 20, marginTop: 4 }}>
                      {s.risk_factors.map((r, i) => <li key={i} style={{ fontSize: '0.85rem' }}>{r}</li>)}
                    </ul>
                  </div>
                )}
                {s.repayment_plan_months && (
                  <p style={{ fontSize: '0.85rem', color: '#6b7280' }}>Repayment plan: <strong>{s.repayment_plan_months} months</strong></p>
                )}
                {s.is_accepted !== 1 && (
                  <button className="btn btn-success btn-sm" style={{ marginTop: 12 }} onClick={() => handleAccept(s.id)}>Accept Settlement</button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
