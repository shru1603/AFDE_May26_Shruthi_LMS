import { useEffect, useState } from 'react';
import { getBooks, getBorrowers, getTransactions, borrowBook, returnBook } from '../../services/api';

const badgeColor = { Borrowed: '#f59e0b', Returned: '#10b981' };

function getStatus(t) {
  return t.return_date ? 'Returned' : 'Borrowed';
}

export default function BorrowReturn() {
  const [availableBooks, setAvailableBooks] = useState([]);
  const [borrowers, setBorrowers] = useState([]);
  const [activeTransactions, setActiveTransactions] = useState([]);
  const [allTransactions, setAllTransactions] = useState([]);

  const [bookSearch, setBookSearch] = useState('');
  const [selectedBookId, setSelectedBookId] = useState('');
  const [borrowerName, setBorrowerName] = useState('');

  const [txSearch, setTxSearch] = useState('');
  const [returnTxId, setReturnTxId] = useState('');

  const [message, setMessage] = useState({ text: '', type: '' });

  const load = async () => {
    const [booksRes, borrowersRes, txRes] = await Promise.all([
      getBooks(), getBorrowers(), getTransactions(),
    ]);
    setAvailableBooks(booksRes.data.filter((b) => b.availability_status === 'available'));
    setBorrowers(borrowersRes.data);
    const txs = txRes.data;
    setActiveTransactions(txs.filter((t) => !t.return_date));
    setAllTransactions([...txs].sort((a, b) => new Date(b.borrow_date) - new Date(a.borrow_date)));
  };

  useEffect(() => { load(); }, []);

  const filteredBooks = bookSearch.trim()
    ? availableBooks.filter((b) =>
        b.title.toLowerCase().includes(bookSearch.toLowerCase()) ||
        b.author.toLowerCase().includes(bookSearch.toLowerCase())
      )
    : availableBooks;

  const filteredTx = txSearch.trim()
    ? activeTransactions.filter((t) =>
        (t.book_title || '').toLowerCase().includes(txSearch.toLowerCase()) ||
        (t.borrower_name || '').toLowerCase().includes(txSearch.toLowerCase())
      )
    : activeTransactions;

  const handleBorrow = async (e) => {
    e.preventDefault();
    setMessage({ text: '', type: '' });
    const matched = borrowers.find(
      (b) => b.borrower_name.toLowerCase() === borrowerName.trim().toLowerCase()
    );
    if (!matched) {
      setMessage({ text: 'Name not found in borrower records. Contact the librarian to register.', type: 'error' });
      return;
    }
    try {
      await borrowBook({ book_id: Number(selectedBookId), borrower_id: matched.borrower_id });
      setMessage({ text: 'Book borrowed successfully!', type: 'success' });
      setSelectedBookId('');
      setBorrowerName('');
      setBookSearch('');
      load();
    } catch (err) {
      setMessage({ text: err.response?.data?.detail || 'Error borrowing book', type: 'error' });
    }
  };

  const handleReturn = async (e) => {
    e.preventDefault();
    setMessage({ text: '', type: '' });
    try {
      await returnBook({ transaction_id: Number(returnTxId) });
      setMessage({ text: 'Book returned successfully!', type: 'success' });
      setReturnTxId('');
      setTxSearch('');
      load();
    } catch (err) {
      setMessage({ text: err.response?.data?.detail || 'Error returning book', type: 'error' });
    }
  };

  return (
    <div style={styles.page}>
      <h2 style={styles.heading}>Borrow / Return</h2>

      {message.text && (
        <div style={{ ...styles.msg, background: message.type === 'success' ? '#f0fdf4' : '#fef2f2', color: message.type === 'success' ? '#15803d' : '#dc2626', borderLeft: `4px solid ${message.type === 'success' ? '#10b981' : '#ef4444'}` }}>
          {message.text}
        </div>
      )}

      <div style={styles.row}>
        <form onSubmit={handleBorrow} style={styles.box}>
          <h3 style={styles.boxTitle}>Borrow a Book</h3>
          <input
            style={styles.input}
            placeholder="Search by title or author..."
            value={bookSearch}
            onChange={(e) => { setBookSearch(e.target.value); setSelectedBookId(''); }}
          />
          <select style={styles.input} required value={selectedBookId} onChange={(e) => setSelectedBookId(e.target.value)}>
            <option value="">Select a book ({filteredBooks.length} available)...</option>
            {filteredBooks.map((b) => (
              <option key={b.book_id} value={b.book_id}>{b.title} — {b.author}</option>
            ))}
          </select>
          <input
            style={styles.input}
            placeholder="Type your full name"
            required
            value={borrowerName}
            onChange={(e) => setBorrowerName(e.target.value)}
            list="borrower-names"
          />
          <datalist id="borrower-names">
            {borrowers.map((b) => <option key={b.borrower_id} value={b.borrower_name} />)}
          </datalist>
          <button style={styles.borrowBtn} type="submit">Borrow Book</button>
        </form>

        <form onSubmit={handleReturn} style={styles.box}>
          <h3 style={styles.boxTitle}>Return a Book</h3>
          <input
            style={styles.input}
            placeholder="Search by book title or borrower name..."
            value={txSearch}
            onChange={(e) => { setTxSearch(e.target.value); setReturnTxId(''); }}
          />
          <select style={styles.input} required value={returnTxId} onChange={(e) => setReturnTxId(e.target.value)}>
            <option value="">Select your transaction ({filteredTx.length} active)...</option>
            {filteredTx.map((t) => (
              <option key={t.transaction_id} value={t.transaction_id}>
                TX #{t.transaction_id} — "{t.book_title}" by {t.borrower_name}
              </option>
            ))}
          </select>
          <button style={styles.returnBtn} type="submit">Return Book</button>
        </form>
      </div>

      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Transactions</h3>
        {allTransactions.length === 0 ? (
          <p style={{ color: '#94a3b8', fontSize: 15 }}>No transactions yet.</p>
        ) : (
          <div style={styles.tableWrap}>
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
                {allTransactions.map((t, i) => {
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
        )}
      </div>
    </div>
  );
}

const styles = {
  page:       { padding: 32, background: '#f8fafc', minHeight: '100vh' },
  heading:    { fontSize: 24, fontWeight: 700, marginBottom: 24, color: '#0d3b25' },
  msg:        { padding: '12px 16px', borderRadius: 8, marginBottom: 24, fontWeight: 500, fontSize: 14 },
  row:        { display: 'flex', gap: 24, marginBottom: 36, flexWrap: 'wrap' },
  box:        { flex: 1, minWidth: 300, background: '#fff', padding: 24, borderRadius: 12, boxShadow: '0 1px 4px rgba(0,0,0,0.06)', display: 'flex', flexDirection: 'column', gap: 14 },
  boxTitle:   { fontSize: 16, fontWeight: 600, color: '#0d3b25', marginBottom: 4 },
  input:      { padding: '10px 12px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 14, outline: 'none', background: '#fff' },
  borrowBtn:  { padding: '11px 0', background: '#0d3b25', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600, fontSize: 14 },
  returnBtn:  { padding: '11px 0', background: '#10b981', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600, fontSize: 14 },
  section:    {},
  sectionTitle: { fontSize: 17, fontWeight: 600, marginBottom: 14, color: '#0d3b25' },
  tableWrap:  { overflowX: 'auto' },
  table:      { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 10, overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.06)' },
  th:         { background: '#0d3b25', color: '#fff', padding: '12px 16px', textAlign: 'left', fontSize: 13, fontWeight: 600 },
  td:         { padding: '11px 16px', borderBottom: '1px solid #f1f5f9', fontSize: 14, color: '#334155' },
  badge:      { color: '#fff', padding: '3px 10px', borderRadius: 20, fontSize: 12, fontWeight: 600 },
};
