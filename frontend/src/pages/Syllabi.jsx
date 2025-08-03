import React, { useEffect, useState } from 'react';
import { listSyllabi, deleteSyllabus, uploadSyllabus } from '../api';
import FileUpload from '../components/FileUpload';

function Syllabi() {
  const [syllabi, setSyllabi] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  const fetchSyllabi = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listSyllabi();
      setSyllabi(data);
    } catch (e) {
      setError(e.message || 'Failed to fetch syllabi');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSyllabi();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this syllabus?')) return;
    try {
      await deleteSyllabus(id);
      fetchSyllabi();
    } catch (e) {
      alert(e.message || 'Failed to delete syllabus');
    }
  };

  const handleFileUpload = async (file) => {
    setUploading(true);
    setUploadError(null);
    try {
      await uploadSyllabus({
        title: file.name,
        file,
        subject: 'other',
      });
      fetchSyllabi();
    } catch (e) {
      setUploadError(e.message || 'Failed to upload syllabus');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container mx-auto py-12">
      <h2 className="text-3xl font-bold mb-8 text-center">Your Syllabi</h2>
      {loading ? (
        <div className="text-center">Loading...</div>
      ) : error ? (
        <div className="text-center text-red-600">{error}</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white rounded-xl shadow mb-8">
            <thead>
              <tr>
                <th className="py-3 px-4 text-left">Title</th>
                <th className="py-3 px-4 text-left">Status</th>
                <th className="py-3 px-4 text-left">Uploaded</th>
                <th className="py-3 px-4 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {syllabi.length === 0 ? (
                <tr><td colSpan={4} className="text-center py-6">No syllabi found.</td></tr>
              ) : (
                syllabi.map(s => (
                  <tr key={s.id} className="border-t">
                    <td className="py-2 px-4">{s.title}</td>
                    <td className="py-2 px-4">{s.status}</td>
                    <td className="py-2 px-4">{s.created_at ? new Date(s.created_at).toLocaleString() : ''}</td>
                    <td className="py-2 px-4">
                      <button onClick={() => handleDelete(s.id)} className="text-red-600 hover:underline">Delete</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
      <div className="max-w-xl mx-auto">
        <h3 className="text-xl font-semibold mb-4">Upload New Syllabus</h3>
        {uploadError && <div className="bg-red-100 text-red-700 p-2 rounded text-center mb-2">{uploadError}</div>}
        <FileUpload onFileUpload={handleFileUpload} isProcessing={uploading} />
      </div>
    </div>
  );
}

export default Syllabi;