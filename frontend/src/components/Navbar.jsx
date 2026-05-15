import { useState, useRef, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';

const adminLinks = [
  { to: '/admin/dashboard', label: 'Dashboard' },
  { to: '/admin/books', label: 'Books' },
  { to: '/admin/borrowers', label: 'Borrowers' },
  { to: '/admin/transactions', label: 'Transactions' },
];

const userLinks = [
  { to: '/user/search', label: 'Search Books' },
  { to: '/user/borrow-return', label: 'Borrow / Return' },
];

export default function Navbar() {
  const navigate = useNavigate();
  const role = localStorage.getItem('lms_role');
  const links = role === 'admin' ? adminLinks : userLinks;
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const logout = () => {
    localStorage.removeItem('lms_role');
    navigate('/');
  };

  return (
    <nav style={styles.nav}>
      <div style={styles.brand}>LMS</div>

      <div style={styles.links}>
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            style={({ isActive }) => ({ ...styles.link, ...(isActive ? styles.active : {}) })}
          >
            {l.label}
          </NavLink>
        ))}
      </div>

      <div style={styles.profileWrap} ref={ref}>
        <button style={styles.avatar} onClick={() => setOpen((o) => !o)}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        </button>
        {open && (
          <div style={styles.dropdown}>
            <div style={styles.dropdownRole}>
              {role === 'admin' ? 'Administrator' : 'User'}
            </div>
            <div style={styles.divider} />
            <button style={styles.logoutBtn} onClick={logout}>Logout</button>
          </div>
        )}
      </div>
    </nav>
  );
}

const styles = {
  nav: {
    display: 'flex', alignItems: 'center',
    background: 'linear-gradient(to right, #061f14, #0d3b25)',
    padding: '0 28px', height: 56,
    boxShadow: '0 2px 8px rgba(0,0,0,0.25)',
    position: 'sticky', top: 0, zIndex: 100,
  },
  brand: { color: '#fff', fontWeight: 700, fontSize: 20, letterSpacing: 1, marginRight: 'auto' },
  links: { display: 'flex', gap: 4, marginRight: 20 },
  link: {
    color: 'rgba(255,255,255,0.70)', textDecoration: 'none',
    padding: '6px 16px', borderRadius: 20, fontSize: 14, fontWeight: 500,
  },
  active: {
    color: '#fff', background: 'rgba(255,255,255,0.15)',
    border: '1px solid rgba(255,255,255,0.25)', fontWeight: 600,
  },
  profileWrap: { position: 'relative' },
  avatar: {
    width: 34, height: 34, borderRadius: '50%',
    background: 'transparent', border: '1.5px solid rgba(255,255,255,0.45)',
    color: 'rgba(255,255,255,0.85)', cursor: 'pointer',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
  },
  dropdown: {
    position: 'absolute', top: 42, right: 0,
    background: '#fff', borderRadius: 10, minWidth: 160,
    boxShadow: '0 8px 24px rgba(0,0,0,0.15)', overflow: 'hidden',
    border: '1px solid #e2e8f0',
  },
  dropdownRole: {
    padding: '12px 16px', fontSize: 13, fontWeight: 600, color: '#0d3b25',
  },
  divider: { height: 1, background: '#f1f5f9' },
  logoutBtn: {
    width: '100%', padding: '10px 16px', background: 'none',
    border: 'none', textAlign: 'left', cursor: 'pointer',
    fontSize: 13, color: '#64748b', fontWeight: 500,
  },
};
