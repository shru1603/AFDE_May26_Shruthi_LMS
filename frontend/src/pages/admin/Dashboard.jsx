import { useEffect, useState } from 'react';
import { getBooks, getTransactions, getBorrowers } from '../../services/api';

const badgeColor = { Borrowed: '#f59e0b', Returned: '#10b981' };

function getStatus(t) {
  return t.return_date ? 'Returned' : 'Borrowed';
}

export default function Dashboard() {
  const [books, setBooks] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [borrowers, setBorrowers] = useState([]);

  useEffect(() => {
    Promise.all([getBooks(), getTransactions(), getBorrowers()]).then(
      ([booksRes, txRes, borrowersRes]) => {
        setBooks(booksRes.data);
        setTransactions(txRes.data);
        setBorrowers(borrowersRes.data);
      }
    );
  }, []);

  const available = books.filter((b) => b.availability_status === 'available').length;
  const borrowed = books.filter((b) => b.availability_status === 'borrowed').length;

  const overdue = transactions.filter((t) => {
    if (t.return_date) return false;
    const days = (Date.now() - new Date(t.borrow_date)) / (1000 * 60 * 60 * 24);
    return days > 14;
  });

  const recent = [...transactions]
    .sort((a, b) => new Date(b.borrow_date) - new Date(a.borrow_date))
    .slice(0, 5);

  return (
    <div style={styles.page}>
      <h2 style={styles.heading}>Dashboard</h2>

      <div style={styles.cards}>
        <StatCard label="Total Books" value={books.length} color="#0d3b25" />
        <StatCard label="Available" value={available} color="#10b981" />
        <StatCard label="Borrowed" value={borrowed} color="#f59e0b" />
        <StatCard label="Borrowers" value={borrowers.length} color="#6366f1" />
      </div>

      {overdue.length > 0 && (
        <div style={styles.section}>
          <h3 style={{ ...styles.sectionTitle, color: '#ef4444' }}>Overdue Books ({overdue.length})</h3>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>TX ID</th>
                <th style={styles.th}>Book</th>
                <th style={styles.th}>Borrower</th>
                <th style={styles.th}>Borrow Date</th>
              </tr>
            </thead>
            <tbody>
              {overdue.map((t, i) => (
                <tr key={t.transaction_id} style={{ background: i % 2 === 0 ? '#fff' : '#fef2f2' }}>
                  <td style={styles.td}>{t.transaction_id}</td>
                  <td style={styles.td}>{t.book_title || `Book ${t.book_id}`}</td>
                  <td style={styles.td}>{t.borrower_name || `Borrower ${t.borrower_id}`}</td>
                  <td style={styles.td}>{new Date(t.borrow_date).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

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
                    <span style={{ ...styles.badge, background: badgeColor[status] }}>
                      {status}
                    </span>
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

function StatCard({ label, value, color }) {
  return (
    <div style={{ ...styles.card, borderTop: `4px solid ${color}` }}>
      <div style={{ ...styles.cardValue, color }}>{value}</div>
      <div style={styles.cardLabel}>{label}</div>
    </div>
  );
}

const styles = {
  page: { padding: 32, background: '#f8fafc', minHeight: '100vh' },
  heading: { fontSize: 24, fontWeight: 700, marginBottom: 28, color: '#0d3b25' },
  cards: { display: 'flex', gap: 20, marginBottom: 36 },
  card: { flex: 1, background: '#fff', borderRadius: 12, padding: '24px 20px', boxShadow: '0 1px 4px rgba(0,0,0,0.06)', textAlign: 'center' },
  cardValue: { fontSize: 36, fontWeight: 700 },
  cardLabel: { color: '#94a3b8', fontSize: 13, fontWeight: 500, marginTop: 4 },
  section: { marginBottom: 36 },
  sectionTitle: { fontSize: 17, fontWeight: 600, marginBottom: 14, color: '#0d3b25' },
  table: { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 10, overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.06)' },
  th: { background: '#0d3b25', color: '#fff', padding: '12px 16px', textAlign: 'left', fontSize: 13, fontWeight: 600 },
  td: { padding: '11px 16px', borderBottom: '1px solid #f1f5f9', fontSize: 14, color: '#334155' },
  badge: { color: '#fff', padding: '3px 10px', borderRadius: 20, fontSize: 12, fontWeight: 600 },
};
