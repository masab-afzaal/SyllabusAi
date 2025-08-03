import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProfile, logout } from '../api';

function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchProfile() {
      setLoading(true);
      setError(null);
      try {
        const data = await getProfile();
        setProfile(data);
      } catch (e) {
        setError(e.message || 'Failed to load profile');
      } finally {
        setLoading(false);
      }
    }
    fetchProfile();
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (e) {
      setError(e.message || 'Logout failed');
    }
  };

  if (loading) return <div className="container mx-auto py-16 text-center">Loading...</div>;
  if (error) return <div className="container mx-auto py-16 text-center text-red-600">{error}</div>;
  if (!profile) return null;

  return (
    <div className="container mx-auto max-w-md py-16">
      <h2 className="text-3xl font-bold mb-8 text-center">Profile</h2>
      <div className="bg-white rounded-xl shadow p-8 space-y-6">
        <div>
          <span className="font-medium">Username:</span> {profile.username}
        </div>
        <div>
          <span className="font-medium">Email:</span> {profile.email}
        </div>
        <button onClick={handleLogout} className="w-full bg-red-500 text-white py-2 rounded font-semibold hover:bg-red-600 transition mt-6">
          Logout
        </button>
      </div>
    </div>
  );
}

export default Profile;