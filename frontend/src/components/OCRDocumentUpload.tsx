import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert } from './ui/alert';
import { Upload, FileText, Loader2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { API_BASE_URL } from '../constants';

interface OCRResult {
  name?: string;
  dob?: string;
  id_number?: string;
  error?: string;
}

interface OCRDocumentUploadProps {
  onDataExtracted: (data: OCRResult) => void;
  disabled?: boolean;
}

const OCRDocumentUpload: React.FC<OCRDocumentUploadProps> = ({ onDataExtracted, disabled = false }) => {
  const { t } = useTranslation();
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleExtractData = async () => {
    if (!selectedFile) {
      setError(t('Please select a file first'));
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(`${API_BASE_URL}/clients/extract-id`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
      } else {
        onDataExtracted(data);
        setSelectedFile(null);
        const fileInput = document.getElementById('ocr-file-input') as HTMLInputElement;
        if (fileInput) {
          fileInput.value = '';
        }
      }
    } catch (err: any) {
      console.error('OCR extraction error:', err);
      setError(t('Failed to extract data from document. Please try again.'));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4 p-4 border rounded-lg bg-gray-50">
      <div className="flex items-center gap-2">
        <FileText className="h-5 w-5" />
        <Label className="text-sm font-medium">{t('Auto-fill from ID Document')}</Label>
      </div>
      
      <div className="space-y-2">
        <Input
          id="ocr-file-input"
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          disabled={disabled || uploading}
        />
        <p className="text-xs text-gray-500">
          {t('Upload an image of ID card or passport to auto-fill form fields')}
        </p>
      </div>

      {selectedFile && (
        <div className="flex items-center justify-between p-2 bg-white rounded border">
          <span className="text-sm text-gray-700">{selectedFile.name}</span>
          <Button
            type="button"
            size="sm"
            onClick={handleExtractData}
            disabled={disabled || uploading}
          >
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {t('Extracting...')}
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                {t('Extract Data')}
              </>
            )}
          </Button>
        </div>
      )}

      {error && (
        <Alert className="text-red-600">
          {error}
        </Alert>
      )}
    </div>
  );
};

export default OCRDocumentUpload;
