import React from 'react';
import { motion } from 'framer-motion';

const HowItWorks = () => {
  const steps = [
    {
      number: '01',
      title: 'Upload Your Syllabus',
      description: 'Simply drag and drop your syllabus file in PDF, DOCX, or image format. Our system supports multiple file types.',
      icon: 'bi-cloud-upload',
      color: 'from-primary-500 to-primary-600'
    },
    {
      number: '02',
      title: 'AI Analysis',
      description: 'Our advanced AI analyzes your content, extracts key topics, and assesses the complexity of each subject.',
      icon: 'bi-cpu',
      color: 'from-accent-500 to-accent-600'
    },
    {
      number: '03',
      title: 'Personalize Settings',
      description: 'Set your study preferences including daily hours, start date, and academic level for optimal planning.',
      icon: 'bi-sliders',
      color: 'from-success-500 to-success-600'
    },
    {
      number: '04',
      title: 'Get Your Plan',
      description: 'Receive a comprehensive study plan with weekly breakdowns, time estimates, and downloadable schedules.',
      icon: 'bi-calendar-check',
      color: 'from-warning-500 to-warning-600'
    }
  ];

  return (
    <section id="how-it-works" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gray-800 mb-6">
            How It <span className="text-primary-600">Works</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Transform your syllabus into an actionable study plan in just four simple steps.
          </p>
        </motion.div>

        <div className="relative">
          {/* Connection Lines */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-primary-200 via-accent-200 to-success-200 transform -translate-y-1/2"></div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 relative z-10">
            {steps.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                className="text-center"
              >
                <div className="relative mb-8">
                  <div className={`w-20 h-20 bg-gradient-to-br ${step.color} rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg`}>
                    <i className={`bi ${step.icon} text-white text-2xl`}></i>
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-white rounded-full border-4 border-gray-100 flex items-center justify-center">
                    <span className="text-xs font-bold text-gray-600">{step.number}</span>
                  </div>
                </div>
                
                <h3 className="text-xl font-bold text-gray-800 mb-4">{step.title}</h3>
                <p className="text-gray-600 leading-relaxed">{step.description}</p>
              </motion.div>
            ))}
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="text-center mt-16"
        >
          <button className="bg-gradient-to-r from-primary-500 to-accent-500 text-white px-8 py-4 rounded-2xl text-lg font-semibold hover:shadow-2xl hover:scale-105 transition-all duration-300 flex items-center space-x-2 mx-auto">
            <i className="bi bi-rocket-takeoff"></i>
            <span>Start Creating Your Plan</span>
          </button>
        </motion.div>
      </div>
    </section>
  );
};

export default HowItWorks;