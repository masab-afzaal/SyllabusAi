import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getPlan, getPlanDashboard } from '../api';

function PlanDetail() {
  const { planId } = useParams();
  const [plan, setPlan] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const [planData, dashboardData] = await Promise.all([
          getPlan(planId),
          getPlanDashboard(planId),
        ]);
        setPlan(planData);
        setDashboard(dashboardData);
      } catch (e) {
        setError(e.message || 'Failed to load plan');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [planId]);

  if (loading) return <div className="container mx-auto py-16 text-center">Loading...</div>;
  if (error) return <div className="container mx-auto py-16 text-center text-red-600">{error}</div>;
  if (!plan || !dashboard) return null;

  return (
    <div className="container mx-auto py-12">
      <h2 className="text-3xl font-bold mb-4 text-center">{plan.title}</h2>
      <div className="mb-8 text-center">
        <span className="font-semibold">Progress:</span> {dashboard.progress.completion_percentage?.toFixed(1) || 0}%
      </div>
      <div className="mb-8">
        <h3 className="text-xl font-semibold mb-2">Upcoming Sessions</h3>
        <ul className="bg-white rounded-xl shadow p-4">
          {dashboard.progress.pending_sessions === 0 ? (
            <li className="text-gray-500">No upcoming sessions.</li>
          ) : (
            (dashboard.upcoming_sessions || []).map(s => (
              <li key={s.id} className="py-2 border-b last:border-b-0 flex justify-between items-center">
                <span>{s.topic_title || s.topic || 'Session'} ({s.session_type})</span>
                <span>{s.scheduled_date ? new Date(s.scheduled_date).toLocaleString() : ''}</span>
              </li>
            ))
          )}
        </ul>
      </div>
      <div className="mb-8">
        <h3 className="text-xl font-semibold mb-2">Milestones</h3>
        <ul className="bg-white rounded-xl shadow p-4">
          {dashboard.milestones.length === 0 ? (
            <li className="text-gray-500">No milestones.</li>
          ) : (
            dashboard.milestones.map(m => (
              <li key={m.id} className="py-2 border-b last:border-b-0 flex justify-between items-center">
                <span>{m.title} ({m.milestone_type})</span>
                <span>{m.target_date ? new Date(m.target_date).toLocaleDateString() : ''}</span>
              </li>
            ))
          )}
        </ul>
      </div>
      <div>
        <h3 className="text-xl font-semibold mb-2">Recent Completed Sessions</h3>
        <ul className="bg-white rounded-xl shadow p-4">
          {dashboard.recent_sessions.length === 0 ? (
            <li className="text-gray-500">No recent sessions.</li>
          ) : (
            dashboard.recent_sessions.map(s => (
              <li key={s.id} className="py-2 border-b last:border-b-0 flex justify-between items-center">
                <span>{s.topic_title || s.topic || 'Session'} ({s.session_type})</span>
                <span>{s.updated_at ? new Date(s.updated_at).toLocaleString() : ''}</span>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
}

export default PlanDetail;