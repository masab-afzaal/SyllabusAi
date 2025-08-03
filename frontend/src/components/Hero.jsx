import React from 'react';
import { motion } from 'framer-motion';

const Hero = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-accent-50">
        {/* Background pattern removed due to encoding issues */}
      </div>

      {/* Floating Elements */}
      <motion.div 
        animate={{ 
          y: [0, -20, 0],
          rotate: [0, 5, 0]
        }}
        transition={{ 
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute top-20 left-10 w-16 h-16 bg-gradient-to-br from-primary-400 to-primary-600 rounded-2xl opacity-20"
      />
      <motion.div 
        animate={{ 
          y: [0, 15, 0],
          rotate: [0, -3, 0]
        }}
        transition={{ 
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1
        }}
        className="absolute top-40 right-20 w-12 h-12 bg-gradient-to-br from-accent-400 to-accent-600 rounded-xl opacity-20"
      />
      <motion.div 
        animate={{ 
          y: [0, -10, 0],
          x: [0, 5, 0]
        }}
        transition={{ 
          duration: 7,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 2
        }}
        className="absolute bottom-32 left-1/4 w-8 h-8 bg-gradient-to-br from-success-400 to-success-600 rounded-lg opacity-20"
      />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="bg-gradient-to-r from-primary-600 via-accent-600 to-primary-800 bg-clip-text text-transparent">
              Transform Your
            </span>
            <br />
            <span className="font-serif text-gray-800">Syllabus into Success</span>
          </h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed"
          >
            Upload any syllabus and get an AI-powered study plan with topic breakdown, 
            time estimates, and personalized weekly schedules in seconds.
          </motion.p>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12"
          >
            <button className="bg-gradient-to-r from-primary-500 to-accent-500 text-white px-8 py-4 rounded-2xl text-lg font-semibold hover:shadow-2xl hover:scale-105 transition-all duration-300 flex items-center space-x-2">
              <i className="bi bi-upload"></i>
              <span>Upload Syllabus</span>
            </button>
            <button className="border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-2xl text-lg font-semibold hover:border-primary-500 hover:text-primary-600 transition-all duration-300 flex items-center space-x-2">
              <i className="bi bi-play-circle"></i>
              <span>Watch Demo</span>
            </button>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto"
          >
            <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <i className="bi bi-file-earmark-text text-white text-xl"></i>
              </div>
              <h3 className="font-semibold text-gray-800 mb-2">Smart Analysis</h3>
              <p className="text-gray-600 text-sm">AI extracts key topics and concepts from any syllabus format</p>
            </div>
            
            <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50">
              <div className="w-12 h-12 bg-gradient-to-br from-accent-500 to-accent-600 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <i className="bi bi-clock text-white text-xl"></i>
              </div>
              <h3 className="font-semibold text-gray-800 mb-2">Time Estimation</h3>
              <p className="text-gray-600 text-sm">Accurate study time predictions based on content complexity</p>
            </div>
            
            <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50">
              <div className="w-12 h-12 bg-gradient-to-br from-success-500 to-success-600 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <i className="bi bi-calendar-check text-white text-xl"></i>
              </div>
              <h3 className="font-semibold text-gray-800 mb-2">Weekly Plans</h3>
              <p className="text-gray-600 text-sm">Personalized study schedules that fit your pace and goals</p>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};

export default Hero;