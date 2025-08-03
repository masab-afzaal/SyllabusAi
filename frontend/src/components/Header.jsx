import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const Header = () => {
  return (
    <motion.header 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="bg-white/80 backdrop-blur-lg border-b border-gray-200/50 sticky top-0 z-50"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center">
              <i className="bi bi-book text-white text-lg"></i>
            </div>
            <div>
              <Link to="/" className="text-xl font-bold bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">
                Smart Syllabus Summarizer
              </Link>
              <p className="text-xs text-gray-500">AI-Powered Study Planner</p>
            </div>
          </div>
          <nav className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-gray-600 hover:text-primary-600 transition-colors font-medium">Home</Link>
            <Link to="/syllabi" className="text-gray-600 hover:text-primary-600 transition-colors font-medium">Syllabi</Link>
            <Link to="/plans" className="text-gray-600 hover:text-primary-600 transition-colors font-medium">Plans</Link>
            <Link to="/preferences" className="text-gray-600 hover:text-primary-600 transition-colors font-medium">Preferences</Link>
            <Link to="/analysis" className="text-gray-600 hover:text-primary-600 transition-colors font-medium">Analysis</Link>
            <Link to="/profile" className="text-gray-600 hover:text-primary-600 transition-colors font-medium">Profile</Link>
            <Link to="/login" className="bg-gradient-to-r from-primary-500 to-accent-500 text-white px-6 py-2 rounded-lg hover:shadow-lg transition-all duration-300 font-medium">Login</Link>
            <Link to="/register" className="border-2 border-primary-500 text-primary-600 px-6 py-2 rounded-lg hover:bg-primary-50 transition-all duration-300 font-medium">Register</Link>
          </nav>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;