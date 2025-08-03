import React, { useEffect, useState } from 'react';
import { listPlans, deletePlan } from '../api';
import { Link } from 'react-router-dom';

function Plans() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPlans = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listPlans();
      setPlans(data);
    } catch (e) {
      setError(e.message || 'Failed to fetch plans');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlans();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this learning plan?')) return;
    try {
      await deletePlan(id);
      fetchPlans();
    } catch (e) {
      alert(e.message || 'Failed to delete plan');
    }
  };

  return (
    <div className="container mx-auto py-12">
      <h2 className="text-3xl font-bold mb-8 text-center">Your Learning Plans</h2>
      {loading ? (
        <div className="text-center">Loading...</div>
      ) : error ? (
        <div className="text-center text-red-600">{error}</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white rounded-xl shadow mb-8">
            <thead>
              <tr>
                <th className="py-3 px-4 text-left">Title</th>
                <th className="py-3 px-4 text-left">Syllabus</th>
                <th className="py-3 px-4 text-left">Created</th>
                <th className="py-3 px-4 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {plans.length === 0 ? (
                <tr><td colSpan={4} className="text-center py-6">No learning plans found.</td></tr>
              ) : (
                plans.map(p => (
                  <tr key={p.id} className="border-t">
                    <td className="py-2 px-4">
                      <Link to={`/plans/${p.id}`} className="text-primary-600 hover:underline">
                        {p.title}
                      </Link>
                    </td>
                    <td className="py-2 px-4">{p.syllabus_title || (p.syllabus && p.syllabus.title) || ''}</td>
                    <td className="py-2 px-4">{p.created_at ? new Date(p.created_at).toLocaleString() : ''}</td>
                    <td className="py-2 px-4">
                      <button onClick={() => handleDelete(p.id)} className="text-red-600 hover:underline">Delete</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Plans;