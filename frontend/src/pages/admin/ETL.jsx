import { useState } from 'react';
import axios from 'axios';

const API = 'http://localhost:8000';

export default function ETL() {
  const [files, setFiles] = useState({ books: null, borrowers: null, transactions: null });
  const [status, setStatus] = useState(null); // null | 'loading' | 'success' | 'error'
  const [result, setResult] = useState(null);

  const handleFile = (key) => (e) => {
    setFiles((f) => ({ ...f, [key]: e.target.files[0] || null }));
    setStatus(null);
    setResult(null);
  };

  const handleSubmit = async () => {
    const anySelected = files.books || files.borrowers || files.transactions;
    if (!anySelected) {
      setStatus('error');
      setResult({ message: 'Please select at least one CSV file to upload.' });
      return;
    }

    setStatus('loading');
    const form = new FormData();
    if (files.books)        form.append('books_csv', files.books);
    if (files.borrowers)    form.append('borrowers_csv', files.borrowers);
    if (files.transactions) form.append('transactions_csv', files.transactions);

    try {
      const res = await axios.post(`${API}/etl/upload`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      if (res.data.status === 'success') {
        setStatus('success');
        setResult(res.data);
      } else {
        setStatus('error');
        setResult(res.data);
      }
    } catch (err) {
      setStatus('error');
      setResult({ message: err.response?.data?.detail || err.message });
    }
  };

  const reset = () => {
    setFiles({ books: null, borrowers: null, transactions: null });
    setStatus(null);
    setResult(null);
    document.querySelectorAll('input[type=file]').forEach((el) => (el.value = ''));
  };

  return (
    <div style={styles.page}>
      <h2 style={styles.heading}>Import CSV Data</h2>
      <p style={styles.subtext}>
        Upload CSV files to import historical data. Only the uploaded files will be processed
        and merged with existing records.
      </p>

      <div style={styles.card}>
        <h3 style={styles.cardTitle}>Select Files to Import</h3>
        <p style={styles.hint}>Upload one or more files. Only the uploaded files will be processed.</p>

        <div style={styles.uploadList}>
          <FileRow label="Books CSV" hint="book_id, isbn, Title, Authors, Category …" onChange={handleFile('books')} file={files.books} />
          <FileRow label="Borrowers CSV" hint="borrower_id, borrower_name, email, phone" onChange={handleFile('borrowers')} file={files.borrowers} />
          <FileRow label="Transactions CSV" hint="transaction_id, book_id, borrower_id, borrow_date, return_date" onChange={handleFile('transactions')} file={files.transactions} />
        </div>

        <div style={styles.actions}>
          <button style={styles.btnSecondary} onClick={reset} disabled={status === 'loading'}>
            Clear
          </button>
          <button style={styles.btnPrimary} onClick={handleSubmit} disabled={status === 'loading'}>
            {status === 'loading' ? 'Running ETL…' : 'Upload & Import'}
          </button>
        </div>
      </div>

      {status === 'success' && result && (
        <div style={{ ...styles.resultCard, borderLeft: '4px solid #10b981' }}>
          <p style={{ ...styles.resultTitle, color: '#10b981' }}>ETL completed successfully</p>
          <p style={styles.resultLine}>Files uploaded: <strong>{result.uploaded.join(', ')}</strong></p>

          <div style={styles.summaryGrid}>
            <SummaryItem label="Books" value={result.summary.books} />
            <SummaryItem label="Borrowers" value={result.summary.borrowers} />
            <SummaryItem label="Transactions" value={result.summary.transactions} />
            <SummaryItem label="Overdue" value={result.summary.overdue} />
          </div>

          {result.transform_stats && Object.keys(result.transform_stats).length > 0 && (
            <div style={{ marginTop: 20 }}>
              <p style={styles.statsTitle}>Transform — Row Breakdown</p>
              <table style={styles.statsTable}>
                <thead>
                  <tr>
                    <th style={styles.sTh}>File</th>
                    <th style={styles.sTh}>Input</th>
                    <th style={styles.sTh}>Loaded</th>
                    <th style={styles.sTh}>Dropped</th>
                    <th style={styles.sTh}>Reasons</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(result.transform_stats).map(([file, s]) => {
                    const reasons = Object.entries(s.dropped)
                      .filter(([, v]) => v > 0)
                      .map(([k, v]) => `${k.replace(/_/g, ' ')}: ${v}`)
                      .join(' · ');
                    const dropped = s.input_rows - s.output_rows;
                    return (
                      <tr key={file}>
                        <td style={styles.sTd}><strong>{file}</strong></td>
                        <td style={styles.sTd}>{s.input_rows}</td>
                        <td style={{ ...styles.sTd, color: '#10b981', fontWeight: 600 }}>{s.output_rows}</td>
                        <td style={{ ...styles.sTd, color: dropped > 0 ? '#ef4444' : '#94a3b8' }}>{dropped}</td>
                        <td style={{ ...styles.sTd, color: '#64748b', fontSize: 12 }}>{reasons || '—'}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          <p style={{ ...styles.hint, marginTop: 16 }}>Go to Dashboard to see the updated analytics charts.</p>
        </div>
      )}

      {status === 'error' && result && (
        <div style={{ ...styles.resultCard, borderLeft: '4px solid #ef4444' }}>
          <p style={{ ...styles.resultTitle, color: '#ef4444' }}>Import failed</p>
          <p style={styles.resultLine}>{result.message}</p>
        </div>
      )}
    </div>
  );
}

function FileRow({ label, hint, onChange, file }) {
  return (
    <div style={styles.fileRow}>
      <div style={styles.fileLabel}>
        <span style={styles.fileLabelText}>{label}</span>
        <span style={styles.fileHint}>{hint}</span>
      </div>
      <label style={{ ...styles.fileBtn, ...(file ? styles.fileBtnSelected : {}) }}>
        {file ? file.name : 'Choose file'}
        <input type="file" accept=".csv" onChange={onChange} style={{ display: 'none' }} />
      </label>
    </div>
  );
}

function SummaryItem({ label, value }) {
  return (
    <div style={styles.summaryItem}>
      <div style={styles.summaryValue}>{value}</div>
      <div style={styles.summaryLabel}>{label}</div>
    </div>
  );
}

const styles = {
  page:           { padding: 32, background: '#f8fafc', minHeight: '100vh' },
  heading:        { fontSize: 24, fontWeight: 700, marginBottom: 8, color: '#0d3b25' },
  subtext:        { color: '#64748b', fontSize: 14, marginBottom: 28, maxWidth: 600 },
  card:           { background: '#fff', borderRadius: 12, padding: '28px 32px', boxShadow: '0 1px 4px rgba(0,0,0,0.07)', maxWidth: 700 },
  cardTitle:      { fontSize: 17, fontWeight: 600, color: '#0d3b25', marginBottom: 4, marginTop: 0 },
  hint:           { fontSize: 13, color: '#94a3b8', marginBottom: 24 },
  uploadList:     { display: 'flex', flexDirection: 'column', gap: 16, marginBottom: 28 },
  fileRow:        { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 16px', background: '#f8fafc', borderRadius: 8, border: '1px solid #e2e8f0' },
  fileLabel:      { display: 'flex', flexDirection: 'column', gap: 2 },
  fileLabelText:  { fontSize: 14, fontWeight: 600, color: '#334155' },
  fileHint:       { fontSize: 12, color: '#94a3b8' },
  fileBtn:        { padding: '7px 16px', background: '#fff', border: '1.5px solid #cbd5e1', borderRadius: 8, fontSize: 13, color: '#475569', cursor: 'pointer', fontWeight: 500, whiteSpace: 'nowrap' },
  fileBtnSelected:{ background: '#f0fdf4', borderColor: '#10b981', color: '#0d3b25' },
  actions:        { display: 'flex', gap: 12, justifyContent: 'flex-end' },
  btnPrimary:     { padding: '10px 24px', background: '#0d3b25', color: '#fff', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: 'pointer' },
  btnSecondary:   { padding: '10px 20px', background: '#f1f5f9', color: '#475569', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 500, cursor: 'pointer' },
  resultCard:     { marginTop: 24, background: '#fff', borderRadius: 12, padding: '24px 28px', boxShadow: '0 1px 4px rgba(0,0,0,0.07)', maxWidth: 700 },
  resultTitle:    { fontSize: 16, fontWeight: 700, marginBottom: 10, marginTop: 0 },
  resultLine:     { fontSize: 14, color: '#475569', marginBottom: 16 },
  summaryGrid:    { display: 'flex', gap: 16, marginBottom: 16 },
  statsTitle:     { fontSize: 14, fontWeight: 600, color: '#334155', marginBottom: 10 },
  statsTable:     { width: '100%', borderCollapse: 'collapse', fontSize: 13 },
  sTh:            { background: '#f1f5f9', padding: '8px 12px', textAlign: 'left', fontWeight: 600, color: '#475569', borderBottom: '1px solid #e2e8f0' },
  sTd:            { padding: '8px 12px', borderBottom: '1px solid #f1f5f9', color: '#334155' },
  summaryItem:    { flex: 1, background: '#f8fafc', borderRadius: 8, padding: '12px', textAlign: 'center' },
  summaryValue:   { fontSize: 24, fontWeight: 700, color: '#0d3b25' },
  summaryLabel:   { fontSize: 12, color: '#94a3b8', marginTop: 4 },
};
