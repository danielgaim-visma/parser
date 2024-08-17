import React, { useState } from 'react';
import { Upload, FileText, Check, Folder, Download } from 'lucide-react';

const DocxParserDesktop = () => {
  const [files, setFiles] = useState([]);
  const [referenceFile, setReferenceFile] = useState(null);
  const [parseDoc, setParseDoc] = useState(false);
  const [createSummary, setCreateSummary] = useState(false);
  const [parseLevel, setParseLevel] = useState('1');
  const [minCount, setMinCount] = useState('');
  const [maxCount, setMaxCount] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [processedFolders, setProcessedFolders] = useState([]);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const handleReferenceFileChange = (e) => {
    setReferenceFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    if (referenceFile) formData.append('reference_file', referenceFile);
    formData.append('parse_doc', parseDoc);
    formData.append('create_summary', createSummary);
    formData.append('parse_level', parseLevel);
    formData.append('min_count', minCount);
    formData.append('max_count', maxCount);

    try {
      const response = await fetch('/api/process', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setResult({
        batchId: data.batchId,
        message: data.message,
      });
      setProcessedFolders(data.processedFolders);
    } catch (error) {
      console.error('Error:', error);
      setResult({
        batchId: null,
        message: 'An error occurred during processing.',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setFiles([]);
    setReferenceFile(null);
    setParseDoc(false);
    setCreateSummary(false);
    setParseLevel('1');
    setMinCount('');
    setMaxCount('');
    setResult(null);
    setProcessedFolders([]);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="bg-blue-600 p-6 text-white">
          <h1 className="text-3xl font-bold">DOCX Parser</h1>
        </div>
        <div className="p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h2 className="text-xl font-semibold mb-4">Upload Documents</h2>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 flex flex-col items-center justify-center h-32">
                  <Upload className="w-12 h-12 text-gray-400 mb-2" />
                  <span className="text-sm text-gray-500">Choose files or drag here</span>
                  <input type="file" className="hidden" multiple onChange={handleFileChange} />
                </div>
                {files.length > 0 && (
                  <ul className="mt-2 text-sm text-gray-600">
                    {files.map((file, index) => (
                      <li key={index} className="flex items-center">
                        <FileText className="w-4 h-4 mr-2" />
                        {file.name}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <div>
                <h2 className="text-xl font-semibold mb-4">Reference File (Optional)</h2>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 flex flex-col items-center justify-center h-32">
                  <Upload className="w-12 h-12 text-gray-400 mb-2" />
                  <span className="text-sm text-gray-500">Choose CSV or TXT file</span>
                  <input type="file" className="hidden" onChange={handleReferenceFileChange} accept=".csv,.txt" />
                </div>
                {referenceFile && (
                  <p className="mt-2 text-sm text-gray-600">
                    <FileText className="inline w-4 h-4 mr-2" />
                    {referenceFile.name}
                  </p>
                )}
              </div>
            </div>
            <div>
              <h2 className="text-xl font-semibold mb-4">Options</h2>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="form-checkbox h-5 w-5 text-blue-600"
                    checked={parseDoc}
                    onChange={(e) => setParseDoc(e.target.checked)}
                  />
                  <span className="ml-2">Parse Documents</span>
                </label>
                {parseDoc && (
                  <select
                    className="mt-2 w-full p-2 border rounded"
                    value={parseLevel}
                    onChange={(e) => setParseLevel(e.target.value)}
                  >
                    <option value="1">Heading 1</option>
                    <option value="2">Heading 2</option>
                    <option value="3">Heading 3</option>
                  </select>
                )}
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="form-checkbox h-5 w-5 text-blue-600"
                    checked={createSummary}
                    onChange={(e) => setCreateSummary(e.target.checked)}
                  />
                  <span className="ml-2">Create Word Count Summary</span>
                </label>
                {createSummary && (
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    <input
                      type="number"
                      placeholder="Min count"
                      className="p-2 border rounded"
                      value={minCount}
                      onChange={(e) => setMinCount(e.target.value)}
                    />
                    <input
                      type="number"
                      placeholder="Max count"
                      className="p-2 border rounded"
                      value={maxCount}
                      onChange={(e) => setMaxCount(e.target.value)}
                    />
                  </div>
                )}
              </div>
            </div>
            <div className="flex justify-between">
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition duration-200"
                disabled={loading}
              >
                {loading ? 'Processing...' : 'Process'}
              </button>
              <button
                type="button"
                onClick={handleClear}
                className="px-6 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition duration-200"
              >
                Clear
              </button>
            </div>
          </form>
        </div>
        {result && (
          <div className="p-6 bg-gray-100">
            <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4" role="alert">
              <p className="font-bold">Success</p>
              <p>{result.message} Batch ID: {result.batchId}</p>
            </div>
          </div>
        )}
        {processedFolders.length > 0 && (
          <div className="p-6 border-t">
            <h2 className="text-xl font-semibold mb-4">Processed Folders</h2>
            <div className="space-y-4">
              {processedFolders.map((folder, index) => (
                <div key={index} className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <Folder className="w-6 h-6 text-blue-500 mr-3" />
                    <span className="text-lg">{folder.name}</span>
                  </div>
                  <a
                    href={folder.zipUrl}
                    download
                    className="flex items-center px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition duration-200"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download ZIP
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocxParserDesktop;