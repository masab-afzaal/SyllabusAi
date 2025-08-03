import React from 'react';
import { motion } from 'framer-motion';
import PropTypes from 'prop-types';

const StudyPlanDisplay = ({ studyPlan, onDownload, onReset }) => {
  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Easy': return 'bg-success-100 text-success-700 border-success-200';
      case 'Medium': return 'bg-warning-100 text-warning-700 border-warning-200';
      case 'Hard': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getDifficultyIcon = (difficulty) => {
    switch (difficulty) {
      case 'Easy': return 'bi-circle-fill';
      case 'Medium': return 'bi-dash-circle-fill';
      case 'Hard': return 'bi-exclamation-triangle-fill';
      default: return 'bi-circle';
    }
  };

  const groupedByWeek = studyPlan.topics.reduce((acc, topic) => {
    if (!acc[topic.week]) {
      acc[topic.week] = [];
    }
    acc[topic.week].push(topic);
    return acc;
  }, {});

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            Your <span className="text-primary-600">Study Plan</span> is Ready!
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            AI has analyzed your syllabus and created a personalized study schedule tailored to your pace.
          </p>
        </motion.div>

        {/* Summary Cards */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12"
        >
          <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-2xl p-6 border border-primary-200">
            <div className="flex items-center justify-between mb-2">
              <i className="bi bi-clock text-primary-600 text-2xl"></i>
              <span className="text-3xl font-bold text-primary-700">{studyPlan.totalHours}</span>
            </div>
            <h3 className="font-semibold text-primary-800">Total Hours</h3>
            <p className="text-primary-600 text-sm">Estimated study time</p>
          </div>

          <div className="bg-gradient-to-br from-accent-50 to-accent-100 rounded-2xl p-6 border border-accent-200">
            <div className="flex items-center justify-between mb-2">
              <i className="bi bi-calendar-week text-accent-600 text-2xl"></i>
              <span className="text-3xl font-bold text-accent-700">{studyPlan.totalWeeks}</span>
            </div>
            <h3 className="font-semibold text-accent-800">Weeks</h3>
            <p className="text-accent-600 text-sm">Study duration</p>
          </div>

          <div className="bg-gradient-to-br from-success-50 to-success-100 rounded-2xl p-6 border border-success-200">
            <div className="flex items-center justify-between mb-2">
              <i className="bi bi-list-task text-success-600 text-2xl"></i>
              <span className="text-3xl font-bold text-success-700">{studyPlan.topics.length}</span>
            </div>
            <h3 className="font-semibold text-success-800">Topics</h3>
            <p className="text-success-600 text-sm">Key concepts</p>
          </div>

          <div className="bg-gradient-to-br from-warning-50 to-warning-100 rounded-2xl p-6 border border-warning-200">
            <div className="flex items-center justify-between mb-2">
              <i className="bi bi-speedometer2 text-warning-600 text-2xl"></i>
              <span className="text-3xl font-bold text-warning-700">{studyPlan.dailyHours}</span>
            </div>
            <h3 className="font-semibold text-warning-800">Hours/Day</h3>
            <p className="text-warning-600 text-sm">Daily commitment</p>
          </div>
        </motion.div>

        {/* Weekly Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="space-y-8"
        >
          {Object.entries(groupedByWeek).map(([week, topics]) => (
            <div key={week} className="bg-gray-50 rounded-2xl p-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-gray-800">Week {week}</h3>
                <div className="flex items-center space-x-2 text-gray-600">
                  <i className="bi bi-clock"></i>
                  <span className="font-medium">
                    {topics.reduce((sum, topic) => sum + topic.estimatedHours, 0)} hours total
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {topics.map((topic, index) => (
                  <motion.div
                    key={topic.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    className="bg-white rounded-xl p-6 border border-gray-200 hover:shadow-lg transition-all duration-300"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="font-semibold text-gray-800 leading-tight">{topic.title}</h4>
                      <span className={`px-2 py-1 rounded-lg text-xs font-medium border ${getDifficultyColor(topic.difficulty)}`}>
                        <i className={`bi ${getDifficultyIcon(topic.difficulty)} mr-1`}></i>
                        {topic.difficulty}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <i className="bi bi-calendar-day"></i>
                        <span>{topic.day}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <i className="bi bi-clock"></i>
                        <span>{topic.estimatedHours}h</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          ))}
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center mt-12"
        >
          <button 
            onClick={onDownload}
            className="bg-gradient-to-r from-primary-500 to-accent-500 text-white px-8 py-4 rounded-2xl text-lg font-semibold hover:shadow-2xl hover:scale-105 transition-all duration-300 flex items-center space-x-2"
          >
            <i className="bi bi-download"></i>
            <span>Download PDF</span>
          </button>
          <button 
            onClick={onReset}
            className="border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-2xl text-lg font-semibold hover:border-primary-500 hover:text-primary-600 transition-all duration-300 flex items-center space-x-2"
          >
            <i className="bi bi-arrow-clockwise"></i>
            <span>Upload New Syllabus</span>
          </button>
        </motion.div>
      </div>
    </section>
  );
};

StudyPlanDisplay.propTypes = {
  studyPlan: PropTypes.shape({
    totalHours: PropTypes.number.isRequired,
    totalWeeks: PropTypes.number.isRequired,
    topics: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.string.isRequired,
      title: PropTypes.string.isRequired,
      estimatedHours: PropTypes.number.isRequired,
      difficulty: PropTypes.string.isRequired,
      week: PropTypes.number.isRequired,
      day: PropTypes.string.isRequired,
    })).isRequired,
    dailyHours: PropTypes.number.isRequired,
  }).isRequired,
  onDownload: PropTypes.func.isRequired,
  onReset: PropTypes.func.isRequired,
};

export default StudyPlanDisplay;