import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Chip,
  Collapse,
  IconButton,
  Divider,
} from '@mui/material';

import { 
  TrendingUp, 
  TrendingDown, 
  ExpandMore, 
  ExpandLess 
} from '@mui/icons-material';
import { apiService } from '../services/api';
import { PortfolioItem } from '../types';

const Portfolio: React.FC = () => {
  const [portfolio, setPortfolio] = useState<PortfolioItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set());

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

  const toggleCardExpansion = (cardId: number) => {
    const newExpandedCards = new Set(expandedCards);
    if (newExpandedCards.has(cardId)) {
      newExpandedCards.delete(cardId);
    } else {
      newExpandedCards.add(cardId);
    }
    setExpandedCards(newExpandedCards);
  };

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

      {/* Активы в виде карточек */}
      <Box>
        <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
          Активы
        </Typography>
        
        {portfolio.length === 0 ? (
          <Card sx={{ bgcolor: 'background.paper' }}>
            <CardContent>
              <Box textAlign="center" py={4}>
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  Портфель пуст
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Добавьте первую монету в портфель
                </Typography>
              </Box>
            </CardContent>
          </Card>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {portfolio.map((item) => {
              const currentValue = (Number(item.current_price) || 0) * (Number(item.total_quantity) || 0);
              const profit = currentValue - (Number(item.total_spent) || 0);
              const profitPercent = (Number(item.total_spent) || 0) > 0 ? (profit / (Number(item.total_spent) || 0)) * 100 : 0;
              const isExpanded = expandedCards.has(item.id);

              return (
                  <Card 
                    key={item.id}
                    sx={{ 
                      bgcolor: 'background.paper',
                      borderRadius: 3,
                      overflow: 'hidden',
                      cursor: 'pointer',
                      transition: 'transform 0.2s, box-shadow 0.2s',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: 4,
                      }
                    }}>
                    <CardContent 
                      sx={{ p: 3 }}
                      onClick={() => toggleCardExpansion(item.id)}
                    >
                      {/* Основная информация - всегда видна */}
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: isExpanded ? 2 : 0 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          {/* Иконка монеты */}
                          <Box sx={{
                            width: 48,
                            height: 48,
                            borderRadius: '50%',
                            bgcolor: 'primary.main',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            fontWeight: 'bold',
                            fontSize: '1.2rem'
                          }}>
                            {item.symbol.substring(0, 2)}
                          </Box>
                          
                          <Box>
                            <Typography variant="h6" fontWeight="bold">
                              {item.symbol}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                              {item.name}
                            </Typography>
                          </Box>
                        </Box>

                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          {/* Прибыль/убыток */}
                          <Box sx={{ textAlign: 'right' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, justifyContent: 'flex-end' }}>
                              {profit >= 0 ? (
                                <TrendingUp color="success" fontSize="small" />
                              ) : (
                                <TrendingDown color="error" fontSize="small" />
                              )}
                              <Typography
                                variant="h6"
                                color={profit >= 0 ? 'success.main' : 'error.main'}
                                fontWeight="bold"
                              >
                                ${Math.abs(profit).toFixed(2)}
                              </Typography>
                            </Box>
                            <Chip
                              label={`${profit >= 0 ? '+' : ''}${profitPercent.toFixed(1)}%`}
                              size="small"
                              color={profit >= 0 ? 'success' : 'error'}
                              variant="outlined"
                            />
                          </Box>

                          {/* Кнопка раскрытия */}
                          <IconButton size="small">
                            {isExpanded ? <ExpandLess /> : <ExpandMore />}
                          </IconButton>
                        </Box>
                      </Box>

                      {/* Подробная информация - раскрывается */}
                      <Collapse in={isExpanded}>
                        <Divider sx={{ mb: 2 }} />
                        <Box sx={{ 
                          display: 'grid', 
                          gridTemplateColumns: { xs: 'repeat(2, 1fr)', sm: 'repeat(3, 1fr)' }, 
                          gap: 2 
                        }}>
                          <Box>
                            <Typography variant="body2" color="textSecondary" gutterBottom>
                              Количество
                            </Typography>
                            <Typography variant="body1" fontWeight="medium">
                              {Number(item.total_quantity).toFixed(4)}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="body2" color="textSecondary" gutterBottom>
                              Средняя цена
                            </Typography>
                            <Typography variant="body1" fontWeight="medium">
                              ${Number(item.avg_price).toFixed(2)}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="body2" color="textSecondary" gutterBottom>
                              Текущая цена
                            </Typography>
                            <Typography variant="body1" fontWeight="medium">
                              ${Number(item.current_price).toFixed(2)}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="body2" color="textSecondary" gutterBottom>
                              Потрачено
                            </Typography>
                            <Typography variant="body1" fontWeight="medium">
                              ${Number(item.total_spent).toFixed(2)}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="body2" color="textSecondary" gutterBottom>
                              Текущая стоимость
                            </Typography>
                            <Typography variant="body1" fontWeight="medium" color="primary.main">
                              ${currentValue.toFixed(2)}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="body2" color="textSecondary" gutterBottom>
                              Последнее обновление
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                              {item.last_updated ? new Date(item.last_updated).toLocaleString() : 'Никогда'}
                            </Typography>
                          </Box>
                        </Box>
                      </Collapse>
                    </CardContent>
                  </Card>
              );
            })}
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default Portfolio; 