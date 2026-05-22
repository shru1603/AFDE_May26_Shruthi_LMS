import { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
  LineChart, Line,
} from 'recharts';
import { getTransactions } from '../../services/api';
import {
  getAnalyticsSummary, getPopularBooks, getCategoryStats, getMonthlyTrends, getOverdueAnalytics,
} from '../../services/api';

const MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const PIE_COLORS = ['#0d3b25','#10b981','#6366f1','#f59e0b','#ef4444','#3b82f6','#8b5cf6','#ec4899'];

function getStatus(t) {
  return t.return_date ? 'Returned' : 'Borrowed';
}

const badgeColor = { Borrowed: '#f59e0b', Returned: '#10b981' };

export default function Dashboard() {
  const [summary, setSummary]       = useState(null);
  const [transactions, setTx]       = useState([]);
  const [popularBooks, setPopular]  = useState([]);
  const [categoryStats, setCategory]= useState([]);
  const [monthlyTrends, setMonthly] = useState([]);
  const [overdueData, setOverdue]   = useState([]);

  useEffect(() => {
    getTransactions().then(r => setTx(r.data));

    Promise.all([getAnalyticsSummary(), getPopularBooks(10), getCategoryStats(), getMonthlyTrends(), getOverdueAnalytics()]).then(
      ([sumRes, popRes, catRes, monRes, ovRes]) => {
        setSummary(sumRes.data);
        setPopular(popRes.data);
        setCategory(catRes.data.slice(0, 8));
        setMonthly(monRes.data.map(r => ({
          ...r,
          label: `${MONTH_NAMES[r.month - 1]} ${r.year}`,
        })));
        setOverdue(ovRes.data);
      }
    );
  }, []);

  const recent = [...transactions]
    .sort((a, b) => new Date(b.borrow_date) - new Date(a.borrow_date))
    .slice(0, 5);

  const barData = popularBooks.map(b => ({
    name: b.title.length > 20 ? b.title.slice(0, 18) + '…' : b.title,
    borrows: b.borrow_count,
  }));

  return (
    <div style={styles.page}>
      <h2 style={styles.heading}>Dashboard</h2>

      {/* ── Stat cards ── */}
      <div style={styles.cards}>
        <StatCard label="Total Books"    value={summary?.total_books ?? '—'}        color="#0d3b25" sub={summary ? `${summary.available} available · ${summary.borrowed} borrowed` : ''} />
        <StatCard label="Borrowers"      value={summary?.total_borrowers ?? '—'}    color="#6366f1" />
        <StatCard label="Transactions"   value={summary?.total_transactions ?? '—'} color="#3b82f6" />
        <StatCard label="Overdue"        value={summary?.overdue_count ?? '—'}      color="#ef4444" sub="not returned > 14 days" />
      </div>

      {/* ── Analytics section ── */}
      <h3 style={styles.sectionHeading}>Analytics</h3>

      {/* Row 1: Bar + Pie */}
      <div style={styles.chartRow}>
        <div style={styles.chartCard}>
          <p style={styles.chartTitle}>Top 10 Most Borrowed Books</p>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={barData} margin={{ top: 8, right: 16, left: 0, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} angle={-35} textAnchor="end" interval={0} />
              <YAxis tick={{ fontSize: 12, fill: '#64748b' }} allowDecimals={false} />
              <Tooltip
                contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0' }}
                formatter={(v) => [v, 'Borrows']}
              />
              <Bar dataKey="borrows" fill="#0d3b25" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={styles.chartCard}>
          <p style={styles.chartTitle}>Borrows by Category</p>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={categoryStats}
                dataKey="borrow_count"
                nameKey="category"
                cx="50%"
                cy="50%"
                outerRadius={90}
                label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {categoryStats.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(v, n) => [v, n]} />
              <Legend
                formatter={(value) => value.length > 22 ? value.slice(0, 20) + '…' : value}
                wrapperStyle={{ fontSize: 12 }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 2: Line chart */}
      <div style={{ ...styles.chartCard, marginBottom: 32 }}>
        <p style={styles.chartTitle}>Monthly Borrow & Return Trends</p>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={monthlyTrends} margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="label" tick={{ fontSize: 12, fill: '#64748b' }} />
            <YAxis tick={{ fontSize: 12, fill: '#64748b' }} allowDecimals={false} />
            <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0' }} />
            <Legend wrapperStyle={{ fontSize: 13 }} />
            <Line type="monotone" dataKey="borrow_count" name="Borrowed" stroke="#0d3b25" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
            <Line type="monotone" dataKey="return_count" name="Returned" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Row 3: Overdue table from analytics */}
      {overdueData.length > 0 && (
        <div style={styles.section}>
          <h3 style={{ ...styles.sectionTitle, color: '#ef4444' }}>
            Overdue Books ({overdueData.length})
          </h3>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Book</th>
                <th style={styles.th}>Borrower</th>
                <th style={styles.th}>Borrow Date</th>
                <th style={styles.th}>Days Overdue</th>
              </tr>
            </thead>
            <tbody>
              {overdueData.map((r, i) => (
                <tr key={r.transaction_id} style={{ background: i % 2 === 0 ? '#fff' : '#fef2f2' }}>
                  <td style={styles.td}>{r.book_title || `Book ${r.book_id}`}</td>
                  <td style={styles.td}>{r.borrower_name || `Borrower ${r.borrower_id}`}</td>
                  <td style={styles.td}>{new Date(r.borrow_date).toLocaleDateString()}</td>
                  <td style={{ ...styles.td, color: '#ef4444', fontWeight: 600 }}>{r.days_overdue}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Row 4: Recent transactions (live) */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Recent Transactions</h3>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>TX ID</th>
              <th style={styles.th}>Book</th>
              <th style={styles.th}>Borrower</th>
              <th style={styles.th}>Borrow Date</th>
              <th style={styles.th}>Return Date</th>
              <th style={styles.th}>Status</th>
            </tr>
          </thead>
          <tbody>
            {recent.map((t, i) => {
              const status = getStatus(t);
              return (
                <tr key={t.transaction_id} style={{ background: i % 2 === 0 ? '#fff' : '#f8fafc' }}>
                  <td style={styles.td}>{t.transaction_id}</td>
                  <td style={styles.td}>{t.book_title || `Book ${t.book_id}`}</td>
                  <td style={styles.td}>{t.borrower_name || `Borrower ${t.borrower_id}`}</td>
                  <td style={styles.td}>{new Date(t.borrow_date).toLocaleDateString()}</td>
                  <td style={styles.td}>{t.return_date ? new Date(t.return_date).toLocaleDateString() : '—'}</td>
                  <td style={styles.td}>
                    <span style={{ ...styles.badge, background: badgeColor[status] }}>{status}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatCard({ label, value, color, sub }) {
  return (
    <div style={{ ...styles.card, borderTop: `4px solid ${color}` }}>
      <div style={{ ...styles.cardValue, color }}>{value}</div>
      <div style={styles.cardLabel}>{label}</div>
      {sub && <div style={styles.cardSub}>{sub}</div>}
    </div>
  );
}

const styles = {
  page:          { padding: 32, background: '#f8fafc', minHeight: '100vh' },
  heading:       { fontSize: 24, fontWeight: 700, marginBottom: 28, color: '#0d3b25' },
  sectionHeading:{ fontSize: 20, fontWeight: 700, margin: '8px 0 20px', color: '#0d3b25', borderBottom: '2px solid #0d3b25', paddingBottom: 8 },
  cards:         { display: 'flex', gap: 20, marginBottom: 36 },
  card:          { flex: 1, background: '#fff', borderRadius: 12, padding: '24px 20px', boxShadow: '0 1px 4px rgba(0,0,0,0.06)', textAlign: 'center' },
  cardValue:     { fontSize: 36, fontWeight: 700 },
  cardLabel:     { color: '#94a3b8', fontSize: 13, fontWeight: 500, marginTop: 4 },
  cardSub:       { color: '#cbd5e1', fontSize: 11, marginTop: 4 },
  chartRow:      { display: 'flex', gap: 24, marginBottom: 24 },
  chartCard:     { flex: 1, background: '#fff', borderRadius: 12, padding: '20px 24px', boxShadow: '0 1px 4px rgba(0,0,0,0.06)' },
  chartTitle:    { fontSize: 15, fontWeight: 600, color: '#0d3b25', marginBottom: 12, marginTop: 0 },
  section:       { marginBottom: 36 },
  sectionTitle:  { fontSize: 17, fontWeight: 600, marginBottom: 14, color: '#0d3b25' },
  table:         { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 10, overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.06)' },
  th:            { background: '#0d3b25', color: '#fff', padding: '12px 16px', textAlign: 'left', fontSize: 13, fontWeight: 600 },
  td:            { padding: '11px 16px', borderBottom: '1px solid #f1f5f9', fontSize: 14, color: '#334155' },
  badge:         { color: '#fff', padding: '3px 10px', borderRadius: 20, fontSize: 12, fontWeight: 600 },
};
