import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';
import { apiService } from '../services/api';
import { PortfolioItem } from '../types';

const Portfolio: React.FC = () => {
  const [portfolio, setPortfolio] = useState<PortfolioItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Для демонстрации используем тестовый Telegram ID
  const testTelegramId = 1042267533;

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        setLoading(true);
        const data = await apiService.getPortfolio(testTelegramId);
        setPortfolio(data.portfolio);
      } catch (err) {
        setError('Ошибка при загрузке портфеля');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolio();
  }, []);

  const totalValue = portfolio.reduce((sum, item) => sum + (Number(item.total_spent) || 0), 0);
  const totalCurrentValue = portfolio.reduce((sum, item) => sum + ((Number(item.current_price) || 0) * (Number(item.total_quantity) || 0)), 0);
  const totalProfit = totalCurrentValue - totalValue;
  const profitPercentage = totalValue > 0 ? (totalProfit / totalValue) * 100 : 0;

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ color: 'primary.main', mb: 4 }}>
        💼 Портфель
      </Typography>

      {/* Общая статистика */}
      <Card sx={{ 
        bgcolor: 'background.paper', 
        mb: 4, 
        borderRadius: 3,
        overflow: 'hidden'
      }}>
        <CardContent sx={{ p: 3 }}>
          {/* Общая стоимость */}
          <Box sx={{ mb: 3 }}>
            <Typography color="textSecondary" gutterBottom>
              Общая стоимость
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
              ${totalValue.toFixed(2)}
            </Typography>
          </Box>

          {/* Текущая стоимость */}
          <Box sx={{ mb: 3 }}>
            <Typography color="textSecondary" gutterBottom>
              Текущая стоимость
            </Typography>
            <Typography variant="h4" sx={{ 
              fontWeight: 'bold', 
              color: totalCurrentValue > 0 ? 'success.main' : 'text.secondary' 
            }}>
              ${totalCurrentValue.toFixed(2)}
            </Typography>
          </Box>

          {/* Прибыль/Убыток */}
          <Box sx={{ mb: 3 }}>
            <Typography color="textSecondary" gutterBottom>
              Прибыль/Убыток
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h5" sx={{ 
                fontWeight: 'bold', 
                color: totalProfit >= 0 ? 'success.main' : 'error.main' 
              }}>
                {totalProfit >= 0 ? '📈' : '📉'} ${Math.abs(totalProfit).toFixed(2)}
              </Typography>
            </Box>
          </Box>

          {/* Процент изменения */}
          <Box>
            <Typography color="textSecondary" gutterBottom>
              Процент изменения
            </Typography>
            <Typography variant="h5" sx={{ 
              fontWeight: 'bold', 
              color: profitPercentage >= 0 ? 'success.main' : 'error.main' 
            }}>
              {profitPercentage >= 0 ? '+' : ''}{profitPercentage.toFixed(2)}%
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Таблица портфеля */}
      <Card sx={{ bgcolor: 'background.paper' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
            Активы
          </Typography>
          
          {portfolio.length === 0 ? (
            <Box textAlign="center" py={4}>
              <Typography variant="h6" color="textSecondary" gutterBottom>
                Портфель пуст
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Добавьте первую монету в портфель
              </Typography>
            </Box>
          ) : (
            <TableContainer component={Paper} sx={{ bgcolor: 'transparent' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Монета</TableCell>
                    <TableCell align="right">Количество</TableCell>
                    <TableCell align="right">Средняя цена</TableCell>
                    <TableCell align="right">Текущая цена</TableCell>
                    <TableCell align="right">Общая стоимость</TableCell>
                    <TableCell align="right">Прибыль/Убыток</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {portfolio.map((item) => {
                    const currentValue = (Number(item.current_price) || 0) * (Number(item.total_quantity) || 0);
                    const profit = currentValue - (Number(item.total_spent) || 0);
                    const profitPercent = (Number(item.total_spent) || 0) > 0 ? (profit / (Number(item.total_spent) || 0)) * 100 : 0;

                    return (
                      <TableRow key={item.id}>
                        <TableCell>
                          <Box>
                            <Typography variant="subtitle1" fontWeight="bold">
                              {item.symbol}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                              {item.name}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body1">
                            {Number(item.total_quantity).toFixed(4)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body1">
                            ${Number(item.avg_price).toFixed(2)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body1">
                            ${Number(item.current_price).toFixed(2)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body1">
                            ${Number(item.total_spent).toFixed(2)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                            {profit >= 0 ? (
                              <TrendingUp color="success" fontSize="small" />
                            ) : (
                              <TrendingDown color="error" fontSize="small" />
                            )}
                            <Typography
                              variant="body1"
                              color={profit >= 0 ? 'success.main' : 'error.main'}
                            >
                              ${profit.toFixed(2)}
                            </Typography>
                            <Chip
                              label={`${profitPercent.toFixed(1)}%`}
                              size="small"
                              color={profit >= 0 ? 'success' : 'error'}
                              variant="outlined"
                            />
                          </Box>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Portfolio; 