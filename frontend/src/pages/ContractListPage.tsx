import React from 'react';
import { getContracts } from '../lib/api';
import { getClients } from '../modules/legal/api/legalApi';
import ContractList from '../components/contracts/ContractList';
import PageLayout from '../components/layout/PageLayout';

const ContractListPage: React.FC = () => {
  return (
    <PageLayout title="Contracts">
      <ContractList 
        getContracts={getContracts}
        getClients={async () => {
          try {
            return await getClients();
          } catch (error) {
            console.error('Error fetching clients:', error);
            return [];
          }
        }}
        basePath="/contracts"
        module="general"
      />
    </PageLayout>
  );
};

export default ContractListPage;
