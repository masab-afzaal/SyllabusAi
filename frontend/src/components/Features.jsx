import React from 'react';
import { motion } from 'framer-motion';

const Features = () => {
  const features = [
    {
      icon: 'bi-robot',
      title: 'AI-Powered Analysis',
      description: 'Advanced NLP algorithms extract key topics, concepts, and learning objectives from any syllabus format.',
      color: 'from-primary-500 to-primary-600'
    },
    {
      icon: 'bi-speedometer2',
      title: 'Smart Time Estimation',
      description: 'Intelligent algorithms calculate realistic study times based on content complexity and your learning pace.',
      color: 'from-accent-500 to-accent-600'
    },
    {
      icon: 'bi-calendar-check',
      title: 'Personalized Scheduling',
      description: 'Custom weekly plans that adapt to your available study hours and academic deadlines.',
      color: 'from-success-500 to-success-600'
    },
    {
      icon: 'bi-graph-up',
      title: 'Difficulty Assessment',
      description: 'Automatic difficulty rating helps you prioritize challenging topics and allocate time effectively.',
      color: 'from-warning-500 to-warning-600'
    },
    {
      icon: 'bi-file-earmark-pdf',
      title: 'Multiple Formats',
      description: 'Support for PDF, DOCX, DOC, and image files with OCR technology for scanned documents.',
      color: 'from-purple-500 to-purple-600'
    },
    {
      icon: 'bi-download',
      title: 'Export Options',
      description: 'Download your study plan as PDF or sync with your favorite calendar application.',
      color: 'from-indigo-500 to-indigo-600'
    }
  ];

  return (
    <section id="features" className="py-20 bg-gradient-to-br from-gray-50 to-primary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gray-800 mb-6">
            Powerful <span className="text-primary-600">Features</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Our AI-powered platform transforms the way you approach studying with intelligent analysis and personalized planning.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
              className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100"
            >
              <div className={`w-16 h-16 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center mb-6`}>
                <i className={`bi ${feature.icon} text-white text-2xl`}></i>
              </div>
              
              <h3 className="text-xl font-bold text-gray-800 mb-4">{feature.title}</h3>
              <p className="text-gray-600 leading-relaxed">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;