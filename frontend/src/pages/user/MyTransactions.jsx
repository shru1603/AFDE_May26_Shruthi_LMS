import { useEffect, useState } from 'react';
import { getTransactions } from '../../services/api';

const badgeColor = { Borrowed: '#e67e22', Returned: '#27ae60' };

function getStatus(t) {
  return t.return_date ? 'Returned' : 'Borrowed';
}

export default function MyTransactions() {
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    getTransactions().then((r) => setTransactions(r.data));
  }, []);

  return (
    <div style={styles.page}>
      <h2 style={styles.heading}>Transactions</h2>
      {transactions.length === 0 ? (
        <p style={styles.empty}>No transactions yet.</p>
      ) : (
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
            {transactions.map((t) => {
              const status = getStatus(t);
              return (
                <tr key={t.transaction_id}>
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
      )}
    </div>
  );
}

const styles = {
  page: { padding: 32 },
  heading: { fontSize: 24, fontWeight: 700, marginBottom: 24, color: '#2c3e50' },
  empty: { color: '#7f8c8d', fontSize: 15 },
  table: { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.07)' },
  th: { background: '#2c3e50', color: '#fff', padding: '12px 16px', textAlign: 'left', fontSize: 13 },
  td: { padding: '10px 16px', borderBottom: '1px solid #f0f0f0', fontSize: 14 },
  badge: { color: '#fff', padding: '3px 10px', borderRadius: 12, fontSize: 12, fontWeight: 600 },
};
