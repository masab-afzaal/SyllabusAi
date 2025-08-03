import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import PropTypes from 'prop-types';

const FileUpload = ({ onFileUpload, isProcessing }) => {
  const [dragActive, setDragActive] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'image/*': ['.png', '.jpg', '.jpeg']
    },
    multiple: false,
    disabled: isProcessing
  });

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-primary-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            Upload Your <span className="text-primary-600">Syllabus</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Drag and drop your syllabus file or click to browse. We support PDF, DOCX, and image formats.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="relative"
        >
          <div
            {...getRootProps()}
            className={`
              relative border-3 border-dashed rounded-3xl p-12 text-center cursor-pointer
              transition-all duration-300 bg-white/80 backdrop-blur-sm
              ${isDragActive || dragActive 
                ? 'border-primary-400 bg-primary-50/80 scale-105' 
                : 'border-gray-300 hover:border-primary-300 hover:bg-primary-50/50'
              }
              ${isProcessing ? 'pointer-events-none opacity-60' : ''}
            `}
          >
            <input {...getInputProps()} />
            
            <AnimatePresence mode="wait">
              {isProcessing ? (
                <motion.div
                  key="processing"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="flex flex-col items-center"
                >
                  <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-accent-500 rounded-2xl flex items-center justify-center mb-6">
                    <motion.i 
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                      className="bi bi-arrow-clockwise text-white text-2xl"
                    />
                  </div>
                  <h3 className="text-2xl font-semibold text-gray-800 mb-2">Processing Your Syllabus</h3>
                  <p className="text-gray-600">AI is analyzing your content and generating your study plan...</p>
                  <div className="mt-6 w-64 bg-gray-200 rounded-full h-2">
                    <motion.div 
                      className="bg-gradient-to-r from-primary-500 to-accent-500 h-2 rounded-full"
                      initial={{ width: "0%" }}
                      animate={{ width: "100%" }}
                      transition={{ duration: 3, ease: "easeInOut" }}
                    />
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="upload"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="flex flex-col items-center"
                >
                  <motion.div 
                    animate={{ y: [0, -10, 0] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                    className="w-16 h-16 bg-gradient-to-br from-primary-500 to-accent-500 rounded-2xl flex items-center justify-center mb-6"
                  >
                    <i className="bi bi-cloud-upload text-white text-2xl"></i>
                  </motion.div>
                  
                  <h3 className="text-2xl font-semibold text-gray-800 mb-2">
                    {isDragActive ? 'Drop your syllabus here' : 'Upload Your Syllabus'}
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Drag and drop your file here, or click to browse
                  </p>
                  
                  <div className="flex flex-wrap justify-center gap-3 mb-6">
                    {['PDF', 'DOCX', 'DOC', 'JPG', 'PNG'].map((format) => (
                      <span 
                        key={format}
                        className="px-3 py-1 bg-gray-100 text-gray-600 rounded-lg text-sm font-medium"
                      >
                        {format}
                      </span>
                    ))}
                  </div>
                  
                  <button className="bg-gradient-to-r from-primary-500 to-accent-500 text-white px-8 py-3 rounded-xl font-semibold hover:shadow-lg transition-all duration-300">
                    Choose File
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

FileUpload.propTypes = {
  onFileUpload: PropTypes.func.isRequired,
  isProcessing: PropTypes.bool.isRequired,
};

export default FileUpload;