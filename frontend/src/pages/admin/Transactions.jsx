import { useEffect, useState } from 'react';
import { getTransactions } from '../../services/api';

const badgeColor = { Borrowed: '#f59e0b', Returned: '#10b981' };

function getStatus(t) {
  return t.return_date ? 'Returned' : 'Borrowed';
}

export default function Transactions() {
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    getTransactions().then((r) => setTransactions(r.data));
  }, []);

  return (
    <div style={styles.page}>
      <h2 style={styles.heading}>All Transactions</h2>
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
          {transactions.map((t, i) => {
            const status = getStatus(t);
            return (
              <tr key={t.transaction_id} style={{ background: i % 2 === 0 ? '#fff' : '#f8fafc' }}>
                <td style={styles.td}>{t.transaction_id}</td>
                <td style={styles.td}><strong>{t.book_title || `Book ${t.book_id}`}</strong></td>
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
  );
}

const styles = {
  page: { padding: 32, background: '#f8fafc', minHeight: '100vh' },
  heading: { fontSize: 24, fontWeight: 700, marginBottom: 28, color: '#0d3b25' },
  table: { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 10, overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.06)' },
  th: { background: '#0d3b25', color: '#fff', padding: '12px 16px', textAlign: 'left', fontSize: 13, fontWeight: 600 },
  td: { padding: '11px 16px', borderBottom: '1px solid #f1f5f9', fontSize: 14, color: '#334155' },
  badge: { color: '#fff', padding: '3px 10px', borderRadius: 20, fontSize: 12, fontWeight: 600 },
};
