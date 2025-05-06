import React, { useState, useEffect } from 'react';
import { trafficApi } from '../api/trafficApi';

interface Company {
  id: string;
  name: string;
}

interface DMCEManualLoginProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

/**
 * DMCEManualLogin Component
 * 
 * This component provides a manual login fallback for the DMCE portal.
 * It opens a Firefox browser window in Private Browsing mode for manual login.
 */
const DMCEManualLogin: React.FC<DMCEManualLoginProps> = ({ 
  open, 
  onClose,
  onSuccess
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [loginUrl, setLoginUrl] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setLoading(false);
      setError(null);
      setSuccess(false);
      setMessage(null);
      setLoginUrl(null);
      
      loadCompanies();
    }
  }, [open]);

  const loadCompanies = async () => {
    try {
      setCompanies([
        { id: 'Crandon', name: 'Crandon' },
        { id: 'Company2', name: 'Company 2' }
      ]);
      
      setSelectedCompany('Crandon');
    } catch (err) {
      setError('Error loading companies');
      console.error('Error loading companies:', err);
    }
  };

  const handleStartManualLogin = async () => {
    setLoading(true);
    setError(null);
    setMessage(null);
    setLoginUrl(null);
    
    try {
      const response = await trafficApi.startDMCEManualLogin(selectedCompany);
      
      if (response.success) {
        setSuccess(true);
        setMessage(response.message || 'Manual login window opened successfully');
        setLoginUrl(response.loginUrl || null);
      } else {
        setError(response.error || 'Failed to open manual login window');
      }
    } catch (err) {
      setError('Error starting manual login process');
      console.error('Error starting manual login:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCompanyChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCompany(event.target.value);
  };

  const handleCompleteLogin = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await trafficApi.completeDMCEManualLogin();
      
      if (response.success) {
        setSuccess(true);
        setMessage('Login completed successfully');
        
        onSuccess();
        
        setTimeout(() => {
          onClose();
        }, 2000);
      } else {
        setError(response.error || 'Failed to complete login');
      }
    } catch (err) {
      setError('Error completing manual login');
      console.error('Error completing manual login:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div className="modal-overlay" style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div className="modal-content" style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        width: '90%',
        maxWidth: '800px',
        maxHeight: '90vh',
        overflow: 'auto',
        padding: '20px',
        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)'
      }}>
        <div className="modal-header" style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
          borderBottom: '1px solid #eee',
          paddingBottom: '10px'
        }}>
          <h2 style={{ margin: 0 }}>DMCE Manual Login</h2>
          <button 
            onClick={onClose}
            disabled={loading}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '24px',
              cursor: 'pointer',
              color: '#666'
            }}
          >
            &times;
          </button>
        </div>
        
        <div className="modal-body">
          {error && (
            <div className="alert alert-error" style={{
              backgroundColor: '#f8d7da',
              color: '#721c24',
              padding: '12px',
              borderRadius: '4px',
              marginBottom: '16px'
            }}>
              {error}
            </div>
          )}
          
          {success && message && (
            <div className="alert alert-success" style={{
              backgroundColor: '#d4edda',
              color: '#155724',
              padding: '12px',
              borderRadius: '4px',
              marginBottom: '16px'
            }}>
              {message}
            </div>
          )}
          
          <div style={{ marginBottom: '24px' }}>
            <p style={{ marginBottom: '8px' }}>
              This utility will open a Firefox browser window in Private Browsing mode for manual login to the DMCE portal.
            </p>
            <p style={{ color: '#666', fontSize: '14px', marginBottom: '8px' }}>
              The DMCE portal requires Firefox in Private Browsing mode for reliable operation.
            </p>
          </div>
          
          {!loginUrl && (
            <div style={{
              border: '1px solid #ddd',
              borderRadius: '4px',
              padding: '16px',
              marginBottom: '24px',
              backgroundColor: '#f9f9f9'
            }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '16px',
                alignItems: 'center'
              }}>
                <div>
                  <label htmlFor="company-select" style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: 'bold'
                  }}>
                    Company
                  </label>
                  <select
                    id="company-select"
                    value={selectedCompany}
                    onChange={handleCompanyChange}
                    disabled={loading}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      borderRadius: '4px',
                      border: '1px solid #ccc'
                    }}
                  >
                    {companies.map((company) => (
                      <option key={company.id} value={company.id}>
                        {company.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <button
                    onClick={handleStartManualLogin}
                    disabled={loading || !selectedCompany}
                    style={{
                      width: '100%',
                      padding: '10px 16px',
                      backgroundColor: '#1976d2',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: loading ? 'not-allowed' : 'pointer',
                      opacity: loading || !selectedCompany ? 0.7 : 1
                    }}
                  >
                    {loading ? 'Opening Browser...' : 'Open Login Window'}
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {loginUrl && (
            <div style={{
              border: '1px solid #ddd',
              borderRadius: '4px',
              padding: '16px',
              marginBottom: '24px',
              backgroundColor: '#f9f9f9'
            }}>
              <h3 style={{ marginTop: 0, marginBottom: '12px' }}>
                Login Window Opened
              </h3>
              <p style={{ marginBottom: '12px' }}>
                A Firefox browser window has been opened in Private Browsing mode. Please complete the login process in that window.
              </p>
              <p style={{ marginBottom: '16px' }}>
                Once you have successfully logged in, click the "Complete Login" button below.
              </p>
              <div style={{ textAlign: 'center', marginTop: '16px' }}>
                <button
                  onClick={handleCompleteLogin}
                  disabled={loading}
                  style={{
                    padding: '10px 16px',
                    backgroundColor: '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    opacity: loading ? 0.7 : 1
                  }}
                >
                  {loading ? 'Completing...' : 'Complete Login'}
                </button>
              </div>
            </div>
          )}
          
          {message && !loginUrl && (
            <p style={{ color: '#666', fontSize: '14px' }}>
              {message}
            </p>
          )}
        </div>
        
        <div className="modal-footer" style={{
          borderTop: '1px solid #eee',
          paddingTop: '16px',
          display: 'flex',
          justifyContent: 'flex-end'
        }}>
          <button 
            onClick={onClose} 
            disabled={loading}
            style={{
              padding: '8px 16px',
              backgroundColor: '#f0f0f0',
              border: '1px solid #ddd',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default DMCEManualLogin;
