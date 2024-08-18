import React, { useState, useRef, useEffect } from 'react';
import { Upload, FileText, Check, Folder, Download, AlertTriangle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from './Alert';

const DocxParserDesktop = () => {
  const [files, setFiles] = useState([]);
  const [referenceFile, setReferenceFile] = useState(null);
  const [parseDoc, setParseDoc] = useState(false);
  const [createSummary, setCreateSummary] = useState(false);
  const [keywordTag, setKeywordTag] = useState(false);
  const [parseLevel, setParseLevel] = useState('1');
  const [minCount, setMinCount] = useState('');
  const [maxCount, setMaxCount] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [processedFolders, setProcessedFolders] = useState([]);

  const fileInputRef = useRef(null);
  const referenceFileInputRef = useRef(null);

  useEffect(() => {
    return () => {
      fetch('/api/clear', { method: 'POST' })
        .then(response => response.json())
        .then(data => console.log(data.message))
        .catch(error => console.error('Error clearing upload folder:', error));
    };
  }, []);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    const validFiles = selectedFiles.filter(file => file.name.endsWith('.docx'));
    setFiles(validFiles);
    if (validFiles.length !== selectedFiles.length) {
      setError('Some files were not added. Only .docx files are allowed.');
    } else {
      setError(null);
    }
  };

  const handleReferenceFileChange = (e) => {
    const file = e.target.files[0];
    if (file && (file.name.endsWith('.csv') || file.name.endsWith('.txt'))) {
      setReferenceFile(file);
      setError(null);
    } else {
      setReferenceFile(null);
      setError('Invalid reference file. Only .csv or .txt files are allowed.');
    }
  };

  const handleFileDrop = (e) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    const validFiles = droppedFiles.filter(file => file.name.endsWith('.docx'));
    setFiles(prevFiles => [...prevFiles, ...validFiles]);
    if (validFiles.length !== droppedFiles.length) {
      setError('Some files were not added. Only .docx files are allowed.');
    } else {
      setError(null);
    }
  };

  const handleReferenceFileDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && (file.name.endsWith('.csv') || file.name.endsWith('.txt'))) {
      setReferenceFile(file);
      setError(null);
    } else {
      setError('Invalid reference file. Only .csv or .txt files are allowed.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0) {
      setError('Please select at least one DOCX file to process.');
      return;
    }
    if (!parseDoc && !createSummary && !keywordTag) {
      setError('Please select at least one operation (Parse Documents, Create Summary, or Keyword Tag).');
      return;
    }
    setLoading(true);
    setError(null);

    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    if (referenceFile) formData.append('referenceFile', referenceFile);
    formData.append('parseDoc', parseDoc.toString());
    formData.append('createSummary', createSummary.toString());
    formData.append('keywordTag', keywordTag.toString());
    formData.append('parseLevel', parseLevel);

    if (minCount) formData.append('minCount', minCount);
    if (maxCount) formData.append('maxCount', maxCount);

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        setResult({
          batchId: data.batchId,
          message: data.message,
        });
        setProcessedFolders(data.processedFolders);
      } else {
        throw new Error(data.error || 'An error occurred during processing.');
      }
    } catch (error) {
      console.error('Error:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setFiles([]);
    setReferenceFile(null);
    setParseDoc(false);
    setCreateSummary(false);
    setKeywordTag(false);
    setParseLevel('1');
    setMinCount('');
    setMaxCount('');
    setResult(null);
    setError(null);
    setProcessedFolders([]);

    fetch('/api/clear', { method: 'POST' })
      .then(response => response.json())
      .then(data => console.log(data.message))
      .catch(error => console.error('Error clearing upload folder:', error));
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
                <div
                  className="border-2 border-dashed border-gray-300 rounded-lg p-4 flex flex-col items-center justify-center h-32 cursor-pointer"
                  onClick={() => fileInputRef.current.click()}
                  onDrop={handleFileDrop}
                  onDragOver={(e) => e.preventDefault()}
                >
                  <Upload className="w-12 h-12 text-gray-400 mb-2" />
                  <span className="text-sm text-gray-500">Choose files or drag here</span>
                  <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    multiple
                    onChange={handleFileChange}
                    accept=".docx"
                  />
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
                <div
                  className="border-2 border-dashed border-gray-300 rounded-lg p-4 flex flex-col items-center justify-center h-32 cursor-pointer"
                  onClick={() => referenceFileInputRef.current.click()}
                  onDrop={handleReferenceFileDrop}
                  onDragOver={(e) => e.preventDefault()}
                >
                  <Upload className="w-12 h-12 text-gray-400 mb-2" />
                  <span className="text-sm text-gray-500">Choose CSV or TXT file</span>
                  <input
                    ref={referenceFileInputRef}
                    type="file"
                    className="hidden"
                    onChange={handleReferenceFileChange}
                    accept=".csv,.txt"
                  />
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
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="form-checkbox h-5 w-5 text-blue-600"
                    checked={keywordTag}
                    onChange={(e) => setKeywordTag(e.target.checked)}
                  />
                  <span className="ml-2">Keyword Tag</span>
                </label>
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
        {error && (
          <div className="p-6 bg-red-100">
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          </div>
        )}
        {result && (
          <div className="p-6 bg-gray-100">
            <Alert>
              <Check className="h-4 w-4" />
              <AlertTitle>Success</AlertTitle>
              <AlertDescription>
                {result.message} Batch ID: {result.batchId}
              </AlertDescription>
            </Alert>
          </div>
        )}
        {processedFolders.length > 0 && (
          <div className="p-6 border-t">
            <h2 className="text-xl font-semibold mb-4">Processed Documents</h2>
            <div className="space-y-4">
              {processedFolders.map((folder, index) => (
                <div key={index} className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <Folder className="w-6 h-6 text-blue-500 mr-3" />
                    <span className="text-lg">{folder.output_folder}</span>
                  </div>
                  <a
                    href={folder.zipUrl}
                    download
                    className="flex items-center px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition duration-200"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download All Processed Documents
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