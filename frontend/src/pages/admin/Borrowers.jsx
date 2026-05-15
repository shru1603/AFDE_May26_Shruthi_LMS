import { useEffect, useState } from 'react';
import { getBorrowers, createBorrower, updateBorrower, deleteBorrower } from '../../services/api';

const empty = { borrower_name: '', email: '', phone: '' };
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const phoneRegex = /^\d{10}$/;

export default function Borrowers() {
  const [borrowers, setBorrowers] = useState([]);
  const [form, setForm] = useState(empty);
  const [editId, setEditId] = useState(null);
  const [error, setError] = useState('');

  const load = () => getBorrowers().then((r) => setBorrowers(r.data));
  useEffect(() => { load(); }, []);

  const validate = () => {
    if (!emailRegex.test(form.email)) return 'Enter a valid email address.';
    if (!phoneRegex.test(form.phone)) return 'Phone number must be exactly 10 digits.';
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const validationError = validate();
    if (validationError) { setError(validationError); return; }
    try {
      if (editId) {
        await updateBorrower(editId, form);
      } else {
        await createBorrower(form);
      }
      setForm(empty);
      setEditId(null);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong');
    }
  };

  const handleEdit = (b) => {
    setEditId(b.borrower_id);
    setForm({ borrower_name: b.borrower_name, email: b.email, phone: b.phone });
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this borrower?')) return;
    try {
      await deleteBorrower(id);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Cannot delete this borrower.');
    }
  };

  return (
    <div style={styles.page}>
      <h2 style={styles.heading}>Borrower Management</h2>

      <form onSubmit={handleSubmit} style={styles.form}>
        <h3 style={styles.formTitle}>{editId ? 'Edit Borrower' : 'Add New Borrower'}</h3>
        {error && <p style={styles.error}>{error}</p>}
        <div style={styles.grid}>
          <input
            style={styles.input} placeholder="Full Name" required
            value={form.borrower_name} onChange={(e) => setForm({ ...form, borrower_name: e.target.value })}
          />
          <input
            style={styles.input} placeholder="Email" required
            value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          <input
            style={styles.input} placeholder="Phone (10 digits)" required
            value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value.replace(/\D/g, '').slice(0, 10) })}
          />
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button style={styles.btn} type="submit">{editId ? 'Update' : 'Add Borrower'}</button>
          {editId && <button style={styles.cancelBtn} type="button" onClick={() => { setEditId(null); setForm(empty); setError(''); }}>Cancel</button>}
        </div>
      </form>

      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>ID</th>
            <th style={styles.th}>Name</th>
            <th style={styles.th}>Email</th>
            <th style={styles.th}>Phone</th>
            <th style={styles.th}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {borrowers.map((b, i) => (
            <tr key={b.borrower_id} style={{ background: i % 2 === 0 ? '#fff' : '#f8fafc' }}>
              <td style={styles.td}>{b.borrower_id}</td>
              <td style={styles.td}><strong>{b.borrower_name}</strong></td>
              <td style={styles.td}>{b.email}</td>
              <td style={styles.td}>{b.phone}</td>
              <td style={styles.td}>
                <button style={styles.editBtn} onClick={() => handleEdit(b)}>Edit</button>
                <button style={styles.delBtn} onClick={() => handleDelete(b.borrower_id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const styles = {
  page: { padding: 32, background: '#f8fafc', minHeight: '100vh' },
  heading: { fontSize: 24, fontWeight: 700, marginBottom: 28, color: '#0d3b25' },
  form: { background: '#fff', padding: 24, borderRadius: 12, marginBottom: 28, boxShadow: '0 1px 4px rgba(0,0,0,0.06)' },
  formTitle: { fontSize: 15, fontWeight: 600, marginBottom: 16, color: '#0d3b25' },
  grid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 },
  input: { padding: '10px 12px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 14, outline: 'none' },
  btn: { padding: '10px 24px', background: '#0d3b25', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600 },
  cancelBtn: { padding: '10px 24px', background: '#94a3b8', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer' },
  error: { color: '#ef4444', marginBottom: 12, fontSize: 14 },
  table: { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 10, overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.06)' },
  th: { background: '#0d3b25', color: '#fff', padding: '12px 16px', textAlign: 'left', fontSize: 13, fontWeight: 600 },
  td: { padding: '11px 16px', borderBottom: '1px solid #f1f5f9', fontSize: 14, color: '#334155' },
  editBtn: { marginRight: 8, padding: '5px 14px', background: '#0d3b25', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 13 },
  delBtn: { padding: '5px 14px', background: '#ef4444', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 13 },
};
