import React from 'react';
import { motion } from 'framer-motion';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center">
                <i className="bi bi-book text-white text-lg"></i>
              </div>
              <div>
                <h3 className="text-xl font-bold">Smart Syllabus Summarizer</h3>
                <p className="text-gray-400 text-sm">AI-Powered Study Planner</p>
              </div>
            </div>
            <p className="text-gray-300 mb-6 max-w-md">
              Transform your academic journey with AI-powered syllabus analysis and personalized study planning. 
              Make studying smarter, not harder.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-primary-600 transition-colors">
                <i className="bi bi-twitter"></i>
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-primary-600 transition-colors">
                <i className="bi bi-linkedin"></i>
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-primary-600 transition-colors">
                <i className="bi bi-github"></i>
              </a>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-gray-300">
              <li><a href="#features" className="hover:text-primary-400 transition-colors">Features</a></li>
              <li><a href="#how-it-works" className="hover:text-primary-400 transition-colors">How it Works</a></li>
              <li><a href="#" className="hover:text-primary-400 transition-colors">Pricing</a></li>
              <li><a href="#" className="hover:text-primary-400 transition-colors">API</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-4">Support</h4>
            <ul className="space-y-2 text-gray-300">
              <li><a href="#" className="hover:text-primary-400 transition-colors">Help Center</a></li>
              <li><a href="#" className="hover:text-primary-400 transition-colors">Contact Us</a></li>
              <li><a href="#" className="hover:text-primary-400 transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-primary-400 transition-colors">Terms of Service</a></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm mb-4 md:mb-0">
              © 2025 Smart Syllabus Summarizer. All rights reserved.
            </p>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 1 }}
              className="flex items-center space-x-2 text-sm text-gray-400"
            >
             
            </motion.div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;