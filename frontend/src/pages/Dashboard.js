import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import {
  PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts';

const STRESS_COLORS = {
  LOW: '#16a34a',
  MODERATE: '#f59e0b',
  HIGH: '#ea580c',
  CRITICAL: '#dc2626',
};

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => { fetchDashboard(); }, []);

  const fetchDashboard = async () => {
    try {
      const [overviewRes, insightsRes] = await Promise.all([
        api.get('/api/dashboard/overview'),
        api.get('/api/dashboard/ai-insights'),
      ]);
      setData(overviewRes.data);
      setInsights(insightsRes.data);
    } catch (err) {
      console.error('Dashboard fetch error:', err);
    }
    setLoading(false);
  };

  if (loading) return <div className="loader" style={{ marginTop: 100 }}></div>;
  if (!data) return <div className="empty-state"><p>Failed to load dashboard</p></div>;

  const { summary, loans, financial_profile, active_loans_count } = data;
  const stressLevel = financial_profile.debt_stress_level;

  // Pie chart data for loans
  const pieData = loans.slice(0, 5).map((l) => ({
    name: l.lender_name,
    value: l.outstanding_amount,
  }));
  const PIE_COLORS = ['#2563eb', '#16a34a', '#f59e0b', '#dc2626', '#8b5cf6'];

  return (
    <div>
      <div className="topbar">
        <div>
          <h2>Dashboard</h2>
          <p style={{ color: '#6b7280', fontSize: '0.9rem' }}>Welcome back, {data.user.full_name || data.user.username}! Here's your financial overview.</p>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-4" style={{ marginBottom: 24 }}>
        <div className="stat-card">
          <div className="stat-label">Total Debt</div>
          <div className="stat-value">₹{summary.total_debt.toLocaleString('en-IN')}</div>
        </div>
        <div className="stat-card warning">
          <div className="stat-label">Monthly EMI</div>
          <div className="stat-value">₹{summary.total_emi.toLocaleString('en-IN')}</div>
        </div>
        <div className="stat-card success">
          <div className="stat-label">Monthly Surplus</div>
          <div className="stat-value">₹{summary.monthly_surplus.toLocaleString('en-IN')}</div>
        </div>
        <div className={`stat-card ${stressLevel === 'CRITICAL' || stressLevel === 'HIGH' ? 'danger' : ''}`}>
          <div className="stat-label">Debt Stress</div>
          <div className={`stat-value stress-${stressLevel.toLowerCase()}`} style={{ fontSize: '1.3rem' }}>{stressLevel}</div>
          <div className="stat-change negative">EMI Ratio: {summary.emi_to_income_ratio}%</div>
        </div>
      </div>

      <div className="grid grid-2">
        {/* Debt Distribution Pie Chart */}
        <div className="card">
          <div className="card-header">
            <h3>Debt Distribution</h3>
            <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>{active_loans_count} active loans</span>
          </div>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" outerRadius={100} dataKey="value" label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`} labelLine={false}>
                  {pieData.map((_, idx) => <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(value) => `₹${value.toLocaleString('en-IN')}`} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state"><p>No loans added yet</p><Link to="/loans" className="btn btn-primary btn-sm" style={{ marginTop: 12 }}>Add Loan</Link></div>
          )}
        </div>

        {/* AI Insights */}
        <div className="card">
          <div className="card-header">
            <h3>AI Financial Insights</h3>
            <button className="btn btn-outline btn-sm" onClick={() => setAiLoading(true)} disabled={aiLoading}>
              {aiLoading ? 'Analyzing...' : ' Refresh'}
            </button>
          </div>
          {insights?.insights ? (
            <div>
              <p style={{ marginBottom: 16, padding: 12, background: '#eff6ff', borderRadius: 8, borderLeft: '3px solid #2563eb' }}>
                {insights.insights.summary}
              </p>
              <h4 style={{ fontSize: '0.9rem', marginBottom: 8, color: '#dc2626' }}>⚠️ Risk Factors</h4>
              <ul style={{ paddingLeft: 20, marginBottom: 16 }}>
                {insights.insights.risk_factors.map((r, i) => <li key={i} style={{ fontSize: '0.9rem', marginBottom: 4 }}>{r}</li>)}
              </ul>
              <h4 style={{ fontSize: '0.9rem', marginBottom: 8, color: '#16a34a' }}>✅ Recommendations</h4>
              <ul style={{ paddingLeft: 20 }}>
                {insights.insights.recommendations.map((r, i) => <li key={i} style={{ fontSize: '0.9rem', marginBottom: 4 }}>{r}</li>)}
              </ul>
            </div>
          ) : (
            <div className="empty-state"><p>No insights available yet. Add loans first.</p></div>
          )}
        </div>
      </div>

      {/* Recent Loans Table */}
      <div className="card" style={{ marginTop: 20 }}>
        <div className="card-header">
          <h3>Recent Loans</h3>
          <Link to="/loans" className="btn btn-outline btn-sm">View All</Link>
        </div>
        {loans.length > 0 ? (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Lender</th><th>Type</th><th>Outstanding</th><th>EMI</th><th>Overdue</th><th>Status</th>
                </tr>
              </thead>
              <tbody>
                {loans.slice(0, 5).map((loan) => (
                  <tr key={loan.id}>
                    <td><strong>{loan.lender_name}</strong></td>
                    <td><span className="badge badge-info">{loan.loan_type}</span></td>
                    <td>₹{loan.outstanding_amount.toLocaleString('en-IN')}</td>
                    <td>₹{loan.monthly_emi.toLocaleString('en-IN')}</td>
                    <td>{loan.overdue_months > 0 ? <span className="badge badge-danger">{loan.overdue_months} months</span> : <span className="badge badge-success">Current</span>}</td>
                    <td><span className="badge badge-success">Active</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state"><p>No loans yet. <Link to="/loans" style={{ color: '#2563eb' }}>Add your first loan</Link></p></div>
        )}
      </div>
    </div>
  );
}
