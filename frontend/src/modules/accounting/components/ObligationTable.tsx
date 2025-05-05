import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Box,
  Typography,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  Search as SearchIcon,
  Visibility as VisibilityIcon,
  Payment as PaymentIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { SelectChangeEvent } from '@mui/material/Select';
import { format } from 'date-fns';
import { Obligation } from '../types';

interface ObligationTableProps {
  obligations: Obligation[];
  isLoading: boolean;
  onRefresh: () => void;
  onMakePayment?: (obligationId: number) => void;
}

const ObligationTable: React.FC<ObligationTableProps> = ({
  obligations,
  isLoading,
  onRefresh,
  onMakePayment
}) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [frequencyFilter, setFrequencyFilter] = useState('all');

  const handleViewDetails = (id: number) => {
    navigate(`/accounting/obligations/${id}`);
  };

  const handleMakePayment = (id: number) => {
    if (onMakePayment) {
      onMakePayment(id);
    }
  };

  type ChipColor = 'success' | 'primary' | 'error' | 'default';
  
  const getStatusColor = (status: string): ChipColor => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'pending':
        return 'primary';
      case 'overdue':
        return 'error';
      default:
        return 'default';
    }
  };

  const filteredObligations = obligations.filter(obligation => {
    const matchesSearch = 
      obligation.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (obligation.company_name && obligation.company_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (obligation.tax_type_name && obligation.tax_type_name.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesStatus = statusFilter === 'all' || obligation.status === statusFilter;
    const matchesFrequency = frequencyFilter === 'all' || obligation.frequency === frequencyFilter;
    
    return matchesSearch && matchesStatus && matchesFrequency;
  });

  return (
    <Paper sx={{ p: 2, width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" component="div">
          {t('accounting.obligations.title')}
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={onRefresh}
          startIcon={<RefreshIcon />}
          disabled={isLoading}
        >
          {t('common.buttons.refresh')}
        </Button>
      </Box>
      
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          label={t('common.labels.search')}
          variant="outlined"
          size="small"
          value={searchTerm}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <SearchIcon fontSize="small" sx={{ mr: 1 }} />,
          }}
          sx={{ flexGrow: 1 }}
        />
        
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>{t('accounting.obligations.status')}</InputLabel>
          <Select<string>
            value={statusFilter}
            label={t('accounting.obligations.status')}
            onChange={(e: SelectChangeEvent<string>) => setStatusFilter(e.target.value)}
          >
            <MenuItem value="all">{t('common.filters.all')}</MenuItem>
            <MenuItem value="pending">{t('accounting.obligations.statuses.pending')}</MenuItem>
            <MenuItem value="completed">{t('accounting.obligations.statuses.completed')}</MenuItem>
            <MenuItem value="overdue">{t('accounting.obligations.statuses.overdue')}</MenuItem>
          </Select>
        </FormControl>
        
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>{t('accounting.obligations.frequency')}</InputLabel>
          <Select<string>
            value={frequencyFilter}
            label={t('accounting.obligations.frequency')}
            onChange={(e: SelectChangeEvent<string>) => setFrequencyFilter(e.target.value)}
          >
            <MenuItem value="all">{t('common.filters.all')}</MenuItem>
            <MenuItem value="monthly">{t('accounting.obligations.frequencies.monthly')}</MenuItem>
            <MenuItem value="quarterly">{t('accounting.obligations.frequencies.quarterly')}</MenuItem>
            <MenuItem value="annual">{t('accounting.obligations.frequencies.annual')}</MenuItem>
          </Select>
        </FormControl>
      </Box>
      
      <TableContainer component={Paper} variant="outlined">
        <Table sx={{ minWidth: 650 }} aria-label="obligations table">
          <TableHead>
            <TableRow>
              <TableCell>{t('accounting.obligations.fields.name')}</TableCell>
              <TableCell>{t('accounting.obligations.fields.company')}</TableCell>
              <TableCell>{t('accounting.obligations.fields.taxType')}</TableCell>
              <TableCell>{t('accounting.obligations.fields.frequency')}</TableCell>
              <TableCell>{t('accounting.obligations.fields.nextDueDate')}</TableCell>
              <TableCell>{t('accounting.obligations.fields.status')}</TableCell>
              <TableCell>{t('accounting.obligations.fields.amount')}</TableCell>
              <TableCell align="right">{t('common.labels.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={8} align="center">{t('common.messages.loading')}</TableCell>
              </TableRow>
            ) : filteredObligations.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  {t('accounting.obligations.noObligationsFound')}
                </TableCell>
              </TableRow>
            ) : (
              filteredObligations.map((obligation) => (
                <TableRow key={obligation.id}>
                  <TableCell>{obligation.name}</TableCell>
                  <TableCell>{obligation.company_name}</TableCell>
                  <TableCell>{obligation.tax_type_name}</TableCell>
                  <TableCell>
                    <Chip 
                      label={t(`accounting.obligations.frequencies.${obligation.frequency}`)} 
                      size="small" 
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    {format(new Date(obligation.next_due_date), 'MMM dd, yyyy')}
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={t(`accounting.obligations.statuses.${obligation.status}`)} 
                      color={getStatusColor(obligation.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {obligation.amount ? `$${obligation.amount.toFixed(2)}` : t('common.messages.notAvailable')}
                  </TableCell>
                  <TableCell align="right">
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <Tooltip title={t('common.actions.viewDetails')}>
                        <IconButton 
                          size="small" 
                          onClick={() => handleViewDetails(obligation.id)}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      
                      {obligation.status !== 'completed' && (
                        <Tooltip title={t('accounting.obligations.actions.makePayment')}>
                          <IconButton 
                            size="small" 
                            onClick={() => handleMakePayment(obligation.id)}
                            color="primary"
                          >
                            <PaymentIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default ObligationTable;
