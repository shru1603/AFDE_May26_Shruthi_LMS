import { useEffect, useState } from 'react';
import { getBooks } from '../../services/api';

const statusColor = { available: '#10b981', borrowed: '#f59e0b' };

export default function SearchBooks() {
  const [allBooks, setAllBooks] = useState([]);
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [author, setAuthor] = useState('');

  useEffect(() => {
    getBooks().then((r) => setAllBooks(r.data));
  }, []);

  const categories = [...new Set(allBooks.map((b) => b.category))].sort();
  const authors = [...new Set(allBooks.map((b) => b.author))].sort();

  const filtered = allBooks.filter((b) => {
    const q = query.trim().toLowerCase();
    const matchesText =
      !q ||
      b.title.toLowerCase().includes(q) ||
      b.author.toLowerCase().includes(q) ||
      b.category.toLowerCase().includes(q) ||
      b.isbn.toLowerCase().includes(q);
    const matchesCat = !category || b.category === category;
    const matchesAuthor = !author || b.author === author;
    return matchesText && matchesCat && matchesAuthor;
  });

  const hasFilters = query.trim() || category || author;

  return (
    <div style={styles.page}>
      <h2 style={styles.heading}>Search Books</h2>

      <div style={styles.filterBar}>
        <input
          style={styles.searchInput}
          placeholder="Search by title, author, category or ISBN..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select style={styles.select} value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">All Categories</option>
          {categories.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <select style={styles.select} value={author} onChange={(e) => setAuthor(e.target.value)}>
          <option value="">All Authors</option>
          {authors.map((a) => <option key={a} value={a}>{a}</option>)}
        </select>
        {(query || category || author) && (
          <button style={styles.clearBtn} onClick={() => { setQuery(''); setCategory(''); setAuthor(''); }}>
            Clear
          </button>
        )}
      </div>

      {hasFilters && filtered.length === 0 && <p style={styles.empty}>No books found.</p>}

      {hasFilters ? (
        <div style={styles.grid}>
          {filtered.map((b) => (
            <div key={b.book_id} style={styles.card}>
              <div style={styles.cardTitle}>{b.title}</div>
              <div style={styles.cardAuthor}>by {b.author}</div>
              <div style={styles.cardCat}>{b.category}</div>
              <div style={styles.cardIsbn}>ISBN: {b.isbn}</div>
              <span style={{ ...styles.badge, background: statusColor[b.availability_status] || '#94a3b8' }}>
                {b.availability_status.charAt(0).toUpperCase() + b.availability_status.slice(1)}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <p style={styles.hint}>Use the search or filters above to find books.</p>
      )}
    </div>
  );
}

const styles = {
  page: { padding: 32, background: '#f8fafc', minHeight: '100vh' },
  heading: { fontSize: 24, fontWeight: 700, marginBottom: 24, color: '#0d3b25' },
  filterBar: { display: 'flex', gap: 12, marginBottom: 24, flexWrap: 'wrap' },
  searchInput: { flex: 2, minWidth: 220, padding: '10px 16px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 14, outline: 'none', background: '#fff' },
  select: { flex: 1, minWidth: 150, padding: '10px 12px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 14, outline: 'none', background: '#fff' },
  clearBtn: { padding: '10px 20px', background: '#94a3b8', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: 14 },
  empty: { color: '#94a3b8', fontSize: 15 },
  hint: { color: '#94a3b8', fontSize: 15, marginTop: 60, textAlign: 'center' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 20 },
  card: { background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 1px 4px rgba(0,0,0,0.06)', display: 'flex', flexDirection: 'column', gap: 4, borderTop: '3px solid #0d3b25' },
  cardTitle: { fontWeight: 700, fontSize: 15, color: '#0d3b25', marginBottom: 2 },
  cardAuthor: { fontSize: 13, color: '#64748b' },
  cardCat: { fontSize: 12, color: '#155738' },
  cardIsbn: { fontSize: 12, color: '#94a3b8', marginBottom: 8 },
  badge: { color: '#fff', padding: '3px 10px', borderRadius: 20, fontSize: 12, fontWeight: 600, alignSelf: 'flex-start' },
};
