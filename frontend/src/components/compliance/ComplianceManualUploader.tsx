import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import axios from 'axios';

interface ComplianceManualUploaderProps {
  onUploadSuccess?: (data: any) => void;
  onUploadError?: (error: string) => void;
}

const ComplianceManualUploader: React.FC<ComplianceManualUploaderProps> = ({
  onUploadSuccess,
  onUploadError
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      
      if (selectedFile.type !== 'application/pdf') {
        setErrorMessage('Please upload a PDF file');
        setUploadStatus('error');
        if (onUploadError) onUploadError('Invalid file type. Please upload a PDF file.');
        return;
      }
      
      if (selectedFile.size > 10 * 1024 * 1024) {
        setErrorMessage('File size exceeds 10MB limit');
        setUploadStatus('error');
        if (onUploadError) onUploadError('File size exceeds 10MB limit');
        return;
      }
      
      setFile(selectedFile);
      setUploadStatus('idle');
      setErrorMessage('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setErrorMessage('Please select a file first');
      setUploadStatus('error');
      return;
    }

    try {
      setUploading(true);
      setUploadStatus('uploading');
      setUploadProgress(0);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', 'compliance_manual');
      formData.append('document_metadata', JSON.stringify({
        filename: file.name,
        file_size: file.size,
        file_type: file.type,
        uploaded_at: new Date().toISOString()
      }));

      const apiUrl = import.meta.env.VITE_API_URL || '';
      
      const response = await axios.post(
        `${apiUrl}/api/v1/compliance/manual/upload`, 
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / (progressEvent.total || 100)
            );
            setUploadProgress(percentCompleted);
          },
        }
      );

      setUploadStatus('success');
      if (onUploadSuccess) onUploadSuccess(response.data);
    } catch (error) {
      console.error('Error uploading compliance manual:', error);
      setUploadStatus('error');
      setErrorMessage('Failed to upload compliance manual');
      if (onUploadError) onUploadError('Failed to upload compliance manual');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card className="w-full shadow-md">
      <CardHeader>
        <CardTitle>Upload Compliance Manual</CardTitle>
        <CardDescription>
          Upload your compliance manual PDF to enable AI-powered compliance automation
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div 
            className={`border-2 border-dashed rounded-lg p-6 text-center ${
              uploadStatus === 'error' ? 'border-red-400 bg-red-50' : 
              uploadStatus === 'success' ? 'border-green-400 bg-green-50' : 
              'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
            } transition-colors duration-200`}
          >
            <input
              type="file"
              id="manual-upload"
              className="hidden"
              accept=".pdf"
              onChange={handleFileChange}
              disabled={uploading}
            />
            <label 
              htmlFor="manual-upload" 
              className="cursor-pointer block"
            >
              {file ? (
                <div className="text-sm">
                  <p className="font-medium">{file.name}</p>
                  <p>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              ) : (
                <div>
                  <svg 
                    className="mx-auto h-12 w-12 text-gray-400" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24" 
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={2} 
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" 
                    />
                  </svg>
                  <p className="mt-1 text-sm text-gray-600">
                    Click to select or drag and drop a PDF file
                  </p>
                  <p className="mt-1 text-xs text-gray-500">
                    PDF only, max 10MB
                  </p>
                </div>
              )}
            </label>
          </div>

          {uploadStatus === 'error' && (
            <div className="text-red-500 text-sm">{errorMessage}</div>
          )}

          {uploadStatus === 'success' && (
            <div className="text-green-500 text-sm">
              Compliance manual uploaded successfully!
            </div>
          )}

          {uploadStatus === 'uploading' && (
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-blue-600 h-2.5 rounded-full" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
              <p className="text-xs text-gray-500 mt-1 text-right">
                {uploadProgress}%
              </p>
            </div>
          )}
        </div>
      </CardContent>
      <CardFooter>
        <Button 
          onClick={handleUpload} 
          disabled={!file || uploading || uploadStatus === 'success'}
          className="w-full"
        >
          {uploading ? 'Uploading...' : 'Upload Manual'}
        </Button>
      </CardFooter>
    </Card>
  );
};

export default ComplianceManualUploader;
