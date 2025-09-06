import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
  ToggleButtonGroup,
  ToggleButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { Leaderboard } from '@mui/icons-material';
import { CoinData } from '../types';

interface TopCoinsProps {
  coins: CoinData[];
  loading: boolean;
  error: string | null;
}

const TopCoins: React.FC<TopCoinsProps> = ({ coins, loading, error }) => {
  const [viewMode, setViewMode] = useState<'market_cap' | 'volume'>('market_cap');

  const formatPrice = (price: number) => {
    if (price >= 1) {
      return `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    } else {
      return `$${price.toFixed(6)}`;
    }
  };

  const formatMarketCap = (marketCap: number) => {
    if (marketCap >= 1e12) {
      return `$${(marketCap / 1e12).toFixed(2)}T`;
    } else if (marketCap >= 1e9) {
      return `$${(marketCap / 1e9).toFixed(2)}B`;
    } else if (marketCap >= 1e6) {
      return `$${(marketCap / 1e6).toFixed(2)}M`;
    } else {
      return `$${marketCap.toLocaleString()}`;
    }
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1e12) {
      return `$${(volume / 1e12).toFixed(2)}T`;
    } else if (volume >= 1e9) {
      return `$${(volume / 1e9).toFixed(2)}B`;
    } else if (volume >= 1e6) {
      return `$${(volume / 1e6).toFixed(2)}M`;
    } else {
      return `$${volume.toLocaleString()}`;
    }
  };

  const getChangeColor = (change: number) => {
    if (change > 0) return 'success.main';
    if (change < 0) return 'error.main';
    return 'text.secondary';
  };

  if (loading) {
    return (
      <Card sx={{ bgcolor: 'background.paper', mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <Leaderboard sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Топ монет</Typography>
          </Box>
          <Box display="flex" justifyContent="center" py={3}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ bgcolor: 'background.paper', mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <Leaderboard sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Топ монет</Typography>
          </Box>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ 
      bgcolor: '#1a252f !important',
      border: 'none !important',
      boxShadow: 'none !important',
      borderRadius: 3,
      mb: 3,
      '& .MuiCardContent-root': {
        backgroundColor: '#1a252f !important',
        border: 'none !important'
      }
    }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center">
            <Leaderboard sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Топ монет</Typography>
          </Box>
          
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={(_, newMode) => newMode && setViewMode(newMode)}
            size="small"
          >
            <ToggleButton value="market_cap">Рыночная кап.</ToggleButton>
            <ToggleButton value="volume">Объем</ToggleButton>
          </ToggleButtonGroup>
        </Box>
        
        {coins.length === 0 ? (
          <Typography color="textSecondary" textAlign="center" py={2}>
            Нет данных о топ монетах
          </Typography>
        ) : (
          <TableContainer component={Paper} sx={{ bgcolor: 'transparent', boxShadow: 'none' }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold', color: 'text.secondary' }}>#</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', color: 'text.secondary' }}>Актив</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', color: 'text.secondary' }}>Цена</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', color: 'text.secondary' }}>
                    {viewMode === 'market_cap' ? 'Рыночная кап.' : 'Объем'}
                  </TableCell>
                  <TableCell sx={{ fontWeight: 'bold', color: 'text.secondary' }}>24ч %</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {coins.map((coin, index) => (
                  <TableRow key={coin.id} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {coin.market_cap_rank || index + 1}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <Avatar
                          src={coin.image}
                          sx={{ width: 24, height: 24, mr: 1 }}
                        >
                          {coin.symbol.charAt(0)}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {coin.symbol}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {coin.name}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {formatPrice(coin.current_price)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {viewMode === 'market_cap' 
                          ? (coin.market_cap ? formatMarketCap(coin.market_cap) : '-')
                          : (coin.total_volume ? formatVolume(coin.total_volume) : '-')
                        }
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {coin.price_change_percentage_24h !== undefined ? (
                        <Chip
                          label={`${coin.price_change_percentage_24h > 0 ? '+' : ''}${coin.price_change_percentage_24h.toFixed(2)}%`}
                          size="small"
                          sx={{
                            bgcolor: getChangeColor(coin.price_change_percentage_24h),
                            color: 'white',
                            fontWeight: 'bold',
                            minWidth: 70,
                          }}
                        />
                      ) : (
                        <Typography variant="body2" color="textSecondary">-</Typography>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
    </Card>
  );
};

export default TopCoins;
