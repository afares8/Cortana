import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
          Tax Obligations
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={onRefresh}
          startIcon={<RefreshIcon />}
          disabled={isLoading}
        >
          Refresh
        </Button>
      </Box>
      
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          label="Search"
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
          <InputLabel>Status</InputLabel>
          <Select
            value={statusFilter}
            label="Status"
            onChange={(e: React.ChangeEvent<{ value: unknown }>) => setStatusFilter(e.target.value as string)}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="completed">Completed</MenuItem>
            <MenuItem value="overdue">Overdue</MenuItem>
          </Select>
        </FormControl>
        
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Frequency</InputLabel>
          <Select
            value={frequencyFilter}
            label="Frequency"
            onChange={(e: React.ChangeEvent<{ value: unknown }>) => setFrequencyFilter(e.target.value as string)}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="monthly">Monthly</MenuItem>
            <MenuItem value="quarterly">Quarterly</MenuItem>
            <MenuItem value="annual">Annual</MenuItem>
          </Select>
        </FormControl>
      </Box>
      
      <TableContainer component={Paper} variant="outlined">
        <Table sx={{ minWidth: 650 }} aria-label="obligations table">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Company</TableCell>
              <TableCell>Tax Type</TableCell>
              <TableCell>Frequency</TableCell>
              <TableCell>Next Due Date</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={8} align="center">Loading...</TableCell>
              </TableRow>
            ) : filteredObligations.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  No obligations found. Try adjusting your filters or add a new obligation.
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
                      label={obligation.frequency.charAt(0).toUpperCase() + obligation.frequency.slice(1)} 
                      size="small" 
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    {format(new Date(obligation.next_due_date), 'MMM dd, yyyy')}
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={obligation.status.charAt(0).toUpperCase() + obligation.status.slice(1)} 
                      color={getStatusColor(obligation.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {obligation.amount ? `$${obligation.amount.toFixed(2)}` : 'N/A'}
                  </TableCell>
                  <TableCell align="right">
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <Tooltip title="View Details">
                        <IconButton 
                          size="small" 
                          onClick={() => handleViewDetails(obligation.id)}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      
                      {obligation.status !== 'completed' && (
                        <Tooltip title="Make Payment">
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
