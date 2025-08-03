const API_BASE = '/api/';

export async function uploadSyllabus({ title, description, file, subject, estimated_duration_weeks }) {
  const formData = new FormData();
  formData.append('title', title);
  if (description) formData.append('description', description);
  formData.append('file', file);
  formData.append('subject', subject);
  if (estimated_duration_weeks) formData.append('estimated_duration_weeks', estimated_duration_weeks);

  const res = await fetch(`${API_BASE}curriculum/syllabi/`, {
    method: 'POST',
    credentials: 'include',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to upload syllabus');
  return await res.json();
}

export async function getSyllabus(syllabusId) {
  const res = await fetch(`${API_BASE}curriculum/syllabi/${syllabusId}/`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch syllabus');
  return await res.json();
}

export async function generateLearningPlan({ syllabus_id, title, schedule_type, daily_study_hours, difficulty_progression, target_completion_date }) {
  const res = await fetch(`${API_BASE}learning_plan/api/v1/learning-plans/generate_plan/`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ syllabus_id, title, schedule_type, daily_study_hours, difficulty_progression, target_completion_date }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Failed to generate learning plan');
  }
  return await res.json();
}

export async function register({ username, email, password }) {
  const res = await fetch(`${API_BASE}auth/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ username, email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Registration failed');
  }
  return await res.json();
}

export async function login({ username, password }) {
  const res = await fetch(`${API_BASE}auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Login failed');
  }
  return await res.json();
}

export async function logout() {
  const res = await fetch(`${API_BASE}auth/logout/`, {
    method: 'POST',
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Logout failed');
  return await res.json();
}

export async function getProfile() {
  const res = await fetch(`${API_BASE}auth/profile/`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch profile');
  return await res.json();
}

export async function listSyllabi() {
  const res = await fetch(`${API_BASE}curriculum/syllabi/`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch syllabi');
  return await res.json();
}

export async function deleteSyllabus(syllabusId) {
  const res = await fetch(`${API_BASE}curriculum/syllabi/${syllabusId}/`, {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to delete syllabus');
  return true;
}

export async function listPlans() {
  const res = await fetch(`${API_BASE}learning_plan/api/v1/learning-plans/`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch plans');
  return await res.json();
}

export async function deletePlan(planId) {
  const res = await fetch(`${API_BASE}learning_plan/api/v1/learning-plans/${planId}/`, {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to delete plan');
  return true;
}

export async function getPlan(planId) {
  const res = await fetch(`${API_BASE}learning_plan/api/v1/learning-plans/${planId}/`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch plan');
  return await res.json();
}

export async function getPlanDashboard(planId) {
  const res = await fetch(`${API_BASE}learning_plan/api/v1/learning-plans/${planId}/dashboard/`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch plan dashboard');
  return await res.json();
}