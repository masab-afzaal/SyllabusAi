import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import Hero from './components/Hero';
import FileUpload from './components/FileUpload';
import Features from './components/Features';
import HowItWorks from './components/HowItWorks';
import StudyPlanDisplay from './components/StudyPlanDisplay';
import Footer from './components/Footer';
import { uploadSyllabus, getSyllabus, generateLearningPlan } from './api';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import Syllabi from './pages/Syllabi';
import Plans from './pages/Plans';
import PlanDetail from './pages/PlanDetail';

function Home() {
  return (
    <>
      <Hero />
      <FileUpload onFileUpload={() => {}} isProcessing={false} />
      <Features />
      <HowItWorks />
    </>
  );
}

function Preferences() {
  return <div className="container mx-auto py-12 text-center text-2xl">Study Preferences (Coming Soon)</div>;
}
function Analysis() {
  return <div className="container mx-auto py-12 text-center text-2xl">Analysis & Insights (Coming Soon)</div>;
}

function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/syllabi" element={<Syllabi />} />
        <Route path="/plans" element={<Plans />} />
        <Route path="/plans/:planId" element={<PlanDetail />} />
        <Route path="/preferences" element={<Preferences />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/analysis" element={<Analysis />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
      <Footer />
    </Router>
  );
}

// Helper: get ISO week number (for topic grouping)
Date.prototype.getWeek = function() {
  const date = new Date(this.getTime());
  date.setHours(0, 0, 0, 0);
  date.setDate(date.getDate() + 4 - (date.getDay() || 7));
  const yearStart = new Date(date.getFullYear(), 0, 1);
  return Math.ceil((((date - yearStart) / 86400000) + 1) / 7);
};

export default App;
