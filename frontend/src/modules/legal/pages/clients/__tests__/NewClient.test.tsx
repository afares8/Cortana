import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '../../../../../i18n';
import NewClient from '../NewClient';

jest.mock('../../../api/legalApi', () => ({
  createClient: jest.fn()
}));

const mockCreateClient = require('../../../api/legalApi').createClient;

global.fetch = jest.fn();

const renderNewClient = () => {
  return render(
    <I18nextProvider i18n={i18n}>
      <BrowserRouter>
        <NewClient />
      </BrowserRouter>
    </I18nextProvider>
  );
};

describe('NewClient', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    (global.fetch as jest.Mock).mockImplementation(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({})
      })
    );
  });

  test('creates client and performs automatic compliance checks', async () => {
    mockCreateClient.mockResolvedValue({ id: 1, name: 'Test Client' });
    
    (global.fetch as jest.Mock).mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          total_score: 2.5,
          risk_level: 'MEDIUM',
          components: {
            client_type: 1,
            country: 1,
            industry: 0.5
          }
        })
      })
    );
    
    (global.fetch as jest.Mock).mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          status: 'completed',
          verification_date: '2024-05-28T04:00:00Z',
          pep_status: 'no_match',
          sanctions_status: 'no_match'
        })
      })
    );

    renderNewClient();
    
    fireEvent.change(screen.getByLabelText(/Client Name/i), {
      target: { value: 'Test Client' }
    });
    
    fireEvent.change(screen.getByLabelText(/Email Address/i), {
      target: { value: 'test@example.com' }
    });
    
    fireEvent.change(screen.getByLabelText(/Phone Number/i), {
      target: { value: '+1 555-123-4567' }
    });
    
    fireEvent.mouseDown(screen.getByLabelText(/Industry/i));
    fireEvent.click(screen.getByText(/Finance/i));
    
    fireEvent.mouseDown(screen.getByLabelText(/Client Type/i));
    fireEvent.click(screen.getByText(/Individual/i));
    
    fireEvent.mouseDown(screen.getByLabelText(/Country/i));
    fireEvent.click(screen.getByText(/Panama/i));
    
    fireEvent.click(screen.getByRole('button', { name: /Create Client/i }));
    
    await waitFor(() => {
      expect(mockCreateClient).toHaveBeenCalledWith({
        name: 'Test Client',
        contact_email: 'test@example.com',
        contact_phone: '+1 555-123-4567',
        address: '',
        industry: 'finance',
        kyc_verified: false,
        notes: '',
        client_type: 'individual',
        country: 'PA'
      });
    });
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/compliance/risk-evaluation'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.any(Object),
          body: expect.stringContaining('client_id')
        })
      );
    });
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/legal/verify-client'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.any(Object),
          body: expect.stringContaining('client_id')
        })
      );
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Client created successfully/i)).toBeInTheDocument();
      expect(screen.getByText(/Risk Level/i)).toBeInTheDocument();
      expect(screen.getByText(/MEDIUM/i)).toBeInTheDocument();
      expect(screen.getByText(/Verification Status/i)).toBeInTheDocument();
    });
  });

  test('handles API errors gracefully', async () => {
    mockCreateClient.mockResolvedValue({ id: 1, name: 'Test Client' });
    
    (global.fetch as jest.Mock).mockImplementationOnce(() => 
      Promise.resolve({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Internal server error' })
      })
    );

    renderNewClient();
    
    fireEvent.change(screen.getByLabelText(/Client Name/i), {
      target: { value: 'Test Client' }
    });
    
    fireEvent.change(screen.getByLabelText(/Email Address/i), {
      target: { value: 'test@example.com' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /Create Client/i }));
    
    await waitFor(() => {
      expect(mockCreateClient).toHaveBeenCalled();
    });
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/compliance/risk-evaluation'),
        expect.any(Object)
      );
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Client created successfully/i)).toBeInTheDocument();
    });
  });
});
