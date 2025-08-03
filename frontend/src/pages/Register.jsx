import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { register } from '../api';

function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await register({ username, email, password });
      navigate('/login');
    } catch (e) {
      setError(e.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto max-w-md py-16">
      <h2 className="text-3xl font-bold mb-8 text-center">Register</h2>
      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow p-8 space-y-6">
        {error && <div className="bg-red-100 text-red-700 p-2 rounded text-center">{error}</div>}
        <div>
          <label className="block mb-2 font-medium">Username</label>
          <input type="text" className="w-full border rounded px-3 py-2" value={username} onChange={e => setUsername(e.target.value)} required />
        </div>
        <div>
          <label className="block mb-2 font-medium">Email</label>
          <input type="email" className="w-full border rounded px-3 py-2" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <div>
          <label className="block mb-2 font-medium">Password</label>
          <input type="password" className="w-full border rounded px-3 py-2" value={password} onChange={e => setPassword(e.target.value)} required />
        </div>
        <button type="submit" className="w-full bg-primary-600 text-white py-2 rounded font-semibold hover:bg-primary-700 transition" disabled={loading}>
          {loading ? 'Registering...' : 'Register'}
        </button>
      </form>
    </div>
  );
}

export default Register;