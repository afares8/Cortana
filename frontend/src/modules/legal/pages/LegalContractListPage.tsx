import React from 'react';
import { getContracts, getClients } from '../api/legalApi';
import ContractList from '../../../components/contracts/ContractList';

const LegalContractListPage: React.FC = () => {
  return (
    <ContractList 
      getContracts={getContracts}
      getClients={getClients}
      basePath="/legal/contracts"
      module="legal"
    />
  );
};

export default LegalContractListPage;
