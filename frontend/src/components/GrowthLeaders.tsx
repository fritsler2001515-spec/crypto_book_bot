import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { TrendingUp } from '@mui/icons-material';
import { CoinData } from '../types';

interface GrowthLeadersProps {
  coins: CoinData[];
  loading: boolean;
  error: string | null;
}

const GrowthLeaders: React.FC<GrowthLeadersProps> = ({ coins, loading, error }) => {
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

  if (loading) {
    return (
      <Card sx={{ bgcolor: 'background.paper', mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <TrendingUp sx={{ mr: 1, color: 'success.main' }} />
            <Typography variant="h6">Лидеры роста</Typography>
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
            <TrendingUp sx={{ mr: 1, color: 'success.main' }} />
            <Typography variant="h6">Лидеры роста</Typography>
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
        <Box display="flex" alignItems="center" mb={2}>
          <TrendingUp sx={{ mr: 1, color: 'success.main' }} />
          <Typography variant="h6">Лидеры роста</Typography>
        </Box>
        
        {coins.length === 0 ? (
          <Typography color="textSecondary" textAlign="center" py={2}>
            Нет данных о лидерах роста
          </Typography>
        ) : (
          <Box>
            {coins.map((coin, index) => (
              <Box
                key={coin.id}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  py: 1.5,
                  borderBottom: index < coins.length - 1 ? '1px solid' : 'none',
                  borderColor: 'divider',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                  <Avatar
                    src={coin.image}
                    sx={{ width: 32, height: 32, mr: 2 }}
                  >
                    {coin.symbol.charAt(0)}
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle2" fontWeight="bold">
                      {coin.symbol}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {coin.name}
                    </Typography>
                  </Box>
                </Box>
                
                <Box sx={{ textAlign: 'right', mr: 2 }}>
                  <Typography variant="subtitle2" fontWeight="bold">
                    {formatPrice(coin.current_price)}
                  </Typography>
                  {coin.market_cap && (
                    <Typography variant="caption" color="textSecondary">
                      {formatMarketCap(coin.market_cap)}
                    </Typography>
                  )}
                </Box>
                
                {coin.price_change_percentage_24h !== undefined && (
                  <Chip
                    label={`+${coin.price_change_percentage_24h.toFixed(2)}%`}
                    size="small"
                    sx={{
                      bgcolor: 'success.main',
                      color: 'white',
                      fontWeight: 'bold',
                      minWidth: 70,
                    }}
                  />
                )}
              </Box>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default GrowthLeaders;
