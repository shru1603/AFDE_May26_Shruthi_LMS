import { useEffect, useState } from 'react';
import { getBooks, createBook, updateBook, deleteBook } from '../../services/api';

const empty = { title: '', author: '', category: '', isbn: '' };

export default function Books() {
  const [books, setBooks] = useState([]);
  const [form, setForm] = useState(empty);
  const [editId, setEditId] = useState(null);
  const [error, setError] = useState('');

  const load = () => getBooks().then((r) => setBooks(r.data));
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (editId) {
        await updateBook(editId, form);
      } else {
        await createBook(form);
      }
      setForm(empty);
      setEditId(null);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong');
    }
  };

  const handleEdit = (book) => {
    setEditId(book.book_id);
    setForm({ title: book.title, author: book.author, category: book.category, isbn: book.isbn });
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this book?')) return;
    try {
      await deleteBook(id);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Cannot delete this book.');
    }
  };

  return (
    <div style={styles.page}>
      <h2 style={styles.heading}>Book Management</h2>

      <form onSubmit={handleSubmit} style={styles.form}>
        <h3 style={styles.formTitle}>{editId ? 'Edit Book' : 'Add New Book'}</h3>
        {error && <p style={styles.error}>{error}</p>}
        <div style={styles.grid}>
          <input style={styles.input} placeholder="Title" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          <input style={styles.input} placeholder="Author" required value={form.author} onChange={(e) => setForm({ ...form, author: e.target.value })} />
          <input style={styles.input} placeholder="Category" required value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
          <input style={styles.input} placeholder="ISBN" required value={form.isbn} onChange={(e) => setForm({ ...form, isbn: e.target.value })} />
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button style={styles.btn} type="submit">{editId ? 'Update Book' : 'Add Book'}</button>
          {editId && <button style={styles.cancelBtn} type="button" onClick={() => { setEditId(null); setForm(empty); setError(''); }}>Cancel</button>}
        </div>
      </form>

      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>ID</th>
            <th style={styles.th}>Title</th>
            <th style={styles.th}>Author</th>
            <th style={styles.th}>Category</th>
            <th style={styles.th}>ISBN</th>
            <th style={styles.th}>Status</th>
            <th style={styles.th}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {books.map((b, i) => (
            <tr key={b.book_id} style={{ background: i % 2 === 0 ? '#fff' : '#f8fafc' }}>
              <td style={styles.td}>{b.book_id}</td>
              <td style={styles.td}><strong>{b.title}</strong></td>
              <td style={styles.td}>{b.author}</td>
              <td style={styles.td}>{b.category}</td>
              <td style={styles.td}>{b.isbn}</td>
              <td style={styles.td}>
                <span style={{ ...styles.badge, background: b.availability_status === 'available' ? '#10b981' : '#f59e0b' }}>
                  {b.availability_status.charAt(0).toUpperCase() + b.availability_status.slice(1)}
                </span>
              </td>
              <td style={styles.td}>
                <button style={styles.editBtn} onClick={() => handleEdit(b)}>Edit</button>
                <button style={styles.delBtn} onClick={() => handleDelete(b.book_id)}>Delete</button>
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
  badge: { color: '#fff', padding: '3px 10px', borderRadius: 20, fontSize: 12, fontWeight: 600 },
  editBtn: { marginRight: 8, padding: '5px 14px', background: '#0d3b25', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 13 },
  delBtn: { padding: '5px 14px', background: '#ef4444', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 13 },
};
