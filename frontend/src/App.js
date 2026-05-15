import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import RoleSelect from './pages/RoleSelect';
import Dashboard from './pages/admin/Dashboard';
import Books from './pages/admin/Books';
import Borrowers from './pages/admin/Borrowers';
import Transactions from './pages/admin/Transactions';
import SearchBooks from './pages/user/SearchBooks';
import BorrowReturn from './pages/user/BorrowReturn';


function WithNav({ children }) {
  return (
    <>
      <Navbar />
      {children}
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RoleSelect />} />

        <Route path="/admin/dashboard" element={<WithNav><Dashboard /></WithNav>} />
        <Route path="/admin/books" element={<WithNav><Books /></WithNav>} />
        <Route path="/admin/borrowers" element={<WithNav><Borrowers /></WithNav>} />
        <Route path="/admin/transactions" element={<WithNav><Transactions /></WithNav>} />

        <Route path="/user/search" element={<WithNav><SearchBooks /></WithNav>} />
        <Route path="/user/borrow-return" element={<WithNav><BorrowReturn /></WithNav>} />


        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
