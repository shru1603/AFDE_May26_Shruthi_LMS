import { useNavigate } from 'react-router-dom';

const roles = [
  {
    key: 'admin',
    title: 'Admin',
    desc: 'Manage books, borrowers, and transactions',
    route: '/admin/dashboard',
  },
  {
    key: 'user',
    title: 'User',
    desc: 'Search, borrow, and return books',
    route: '/user/search',
  },
];

export default function RoleSelect() {
  const navigate = useNavigate();

  const select = (role, route) => {
    localStorage.setItem('lms_role', role);
    navigate(route);
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.logoWrap}>
          <span style={styles.logoText}>LMS</span>
        </div>
        <h1 style={styles.title}>Library Management System</h1>
        <p style={styles.subtitle}>Select your role to continue</p>

        <div style={styles.roleList}>
          {roles.map((r) => (
            <button key={r.key} style={styles.roleCard} onClick={() => select(r.key, r.route)}>
              <div style={styles.roleText}>
                <div style={styles.roleTitle}>{r.title}</div>
                <div style={styles.roleDesc}>{r.desc}</div>
              </div>
              <span style={styles.arrow}>&#8250;</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #f0f4f2 0%, #dceee6 100%)',
  },
  card: {
    background: '#fff',
    borderRadius: 16,
    padding: '48px 44px',
    boxShadow: '0 8px 32px rgba(13,59,37,0.12)',
    textAlign: 'center',
    width: 380,
  },
  logoWrap: {
    width: 64, height: 64, borderRadius: '50%',
    background: 'linear-gradient(135deg, #061f14, #0d3b25)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    margin: '0 auto 20px',
  },
  logoText: { color: '#fff', fontWeight: 700, fontSize: 18, letterSpacing: 1 },
  title: { fontSize: 22, fontWeight: 700, color: '#0d3b25', marginBottom: 6 },
  subtitle: { color: '#64748b', fontSize: 14, marginBottom: 32 },
  roleList: { display: 'flex', flexDirection: 'column', gap: 14 },
  roleCard: {
    display: 'flex', alignItems: 'center', gap: 16,
    padding: '18px 20px', border: '1.5px solid #e2e8f0',
    borderRadius: 12, cursor: 'pointer', background: '#fff',
    textAlign: 'left', outline: 'none',
  },
  roleText: { flex: 1 },
  roleTitle: { fontSize: 15, fontWeight: 700, color: '#0d3b25', marginBottom: 2 },
  roleDesc: { fontSize: 12, color: '#94a3b8' },
  arrow: { fontSize: 22, color: '#0d3b25', flexShrink: 0 },
};
