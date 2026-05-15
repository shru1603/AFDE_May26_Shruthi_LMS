import api from '../api';

// Books
export const getBooks = () => api.get('/books/');
export const getBook = (id) => api.get(`/books/${id}`);
export const createBook = (data) => api.post('/books/', data);
export const updateBook = (id, data) => api.put(`/books/${id}`, data);
export const deleteBook = (id) => api.delete(`/books/${id}`);

// Borrowers
export const getBorrowers = () => api.get('/borrowers/');
export const createBorrower = (data) => api.post('/borrowers/', data);
export const updateBorrower = (id, data) => api.put(`/borrowers/${id}`, data);
export const deleteBorrower = (id) => api.delete(`/borrowers/${id}`);

// Transactions
export const getTransactions = () => api.get('/transactions');
export const borrowBook = (data) => api.post('/borrow', data);
export const returnBook = (data) => api.post('/return', data);

// Search
export const searchBooks = (query) => api.get(`/search?q=${query}`);
