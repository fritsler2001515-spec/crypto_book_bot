import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material';
import {
  AccountBalance as PortfolioIcon,
  TrendingUp as TrendingIcon,
  Add as AddIcon,
  Receipt as TransactionsIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { Portfolio, CoinData } from '../types';
import GrowthLeaders from '../components/GrowthLeaders';
import TopCoins from '../components/TopCoins';

const Dashboard: React.FC = () => {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [growthLeaders, setGrowthLeaders] = useState<CoinData[]>([]);
  const [topCoins, setTopCoins] = useState<CoinData[]>([]);
  const [loading, setLoading] = useState(true);
  const [marketLoading, setMarketLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [marketError, setMarketError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const navigate = useNavigate();

  // Для демонстрации используем тестовый Telegram ID
  const testTelegramId = 1042267533;

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const portfolioData = await apiService.getPortfolio(testTelegramId);
        setPortfolio(portfolioData);
        setRetryCount(0); // Сбрасываем счетчик при успехе
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Ошибка при загрузке данных';
        setError(errorMessage);
        console.error('Dashboard error:', err);
        
        // Автоматический ретрай через 5 секунд, максимум 3 попытки
        if (retryCount < 3) {
          setTimeout(() => {
            setRetryCount(prev => prev + 1);
          }, 5000);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [retryCount]);

  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        setMarketLoading(true);
        setMarketError(null);
        
        // Получаем данные параллельно
        const [leaders, top] = await Promise.all([
          apiService.getGrowthLeaders(5),
          apiService.getTopCoins(10)
        ]);
        
        setGrowthLeaders(leaders);
        setTopCoins(top);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Ошибка при загрузке рыночных данных';
        setMarketError(errorMessage);
        console.error('Market data error:', err);
      } finally {
        setMarketLoading(false);
      }
    };

    fetchMarketData();
  }, []);

  // Расчет показателей портфеля
  const totalSpent = portfolio?.portfolio.reduce((sum, item) => sum + (Number(item.total_spent) || 0), 0) || 0;
  const currentValue = portfolio?.portfolio.reduce((sum, item) => {
    const currentPrice = Number(item.current_price) || 0;
    const quantity = Number(item.total_quantity) || 0;
    return sum + (currentPrice * quantity);
  }, 0) || 0;
  const profitLoss = currentValue - totalSpent;
  const profitLossPercent = totalSpent > 0 ? ((profitLoss / totalSpent) * 100) : 0;
  const totalCoins = portfolio?.portfolio.length || 0;

  const quickActions = [
    {
      title: 'Портфель',
      description: 'Просмотр активов',
      icon: <PortfolioIcon sx={{ fontSize: 40, color: 'primary.main' }} />,
      path: '/portfolio',
    },
    {
      title: 'Добавить монету',
      description: 'Новая покупка',
      icon: <AddIcon sx={{ fontSize: 40, color: 'secondary.main' }} />,
      path: '/add-coin',
    },
    {
      title: 'Транзакции',
      description: 'История операций',
      icon: <TransactionsIcon sx={{ fontSize: 40, color: 'success.main' }} />,
      path: '/transactions',
    },
    {
      title: 'Аналитика',
      description: 'Графики и статистика',
      icon: <TrendingIcon sx={{ fontSize: 40, color: 'warning.main' }} />,
      path: '/portfolio',
    },
  ];

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button 
          variant="contained" 
          onClick={() => setRetryCount(prev => prev + 1)}
          sx={{ mt: 2 }}
        >
          🔄 Попробовать снова
        </Button>
        <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
          Убедитесь, что бэкенд запущен: ./start_app.sh
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ color: 'primary.main', mb: 4 }}>
        📊 Дашборд
      </Typography>

      {/* Статистика портфеля */}
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
              ${totalSpent.toFixed(2)}
            </Typography>
          </Box>

          {/* Текущая стоимость */}
          <Box sx={{ mb: 3 }}>
            <Typography color="textSecondary" gutterBottom>
              Текущая стоимость
            </Typography>
            <Typography variant="h4" sx={{ 
              fontWeight: 'bold', 
              color: currentValue > 0 ? 'success.main' : 'text.secondary' 
            }}>
              ${currentValue.toFixed(2)}
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
                color: profitLoss >= 0 ? 'success.main' : 'error.main' 
              }}>
                {profitLoss >= 0 ? '📈' : '📉'} ${Math.abs(profitLoss).toFixed(2)}
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
              color: profitLossPercent >= 0 ? 'success.main' : 'error.main' 
            }}>
              {profitLossPercent >= 0 ? '+' : ''}{profitLossPercent.toFixed(2)}%
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Рыночные данные */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        📈 Рыночные данные
      </Typography>
      
      {/* Лидеры роста */}
      <GrowthLeaders 
        coins={growthLeaders}
        loading={marketLoading}
        error={marketError}
      />
      
      {/* Топ монет */}
      <TopCoins 
        coins={topCoins}
        loading={marketLoading}
        error={marketError}
      />

      {/* Быстрые действия */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3, mt: 4 }}>
        Быстрые действия
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
        {quickActions.map((action) => (
          <Box sx={{ flex: '1 1 200px', minWidth: 200 }} key={action.title}>
            <Card
              sx={{
                bgcolor: 'background.paper',
                cursor: 'pointer',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                },
              }}
              onClick={() => navigate(action.path)}
            >
              <CardContent sx={{ textAlign: 'center', py: 3 }}>
                <Box sx={{ mb: 2 }}>
                  {action.icon}
                </Box>
                <Typography variant="h6" gutterBottom>
                  {action.title}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {action.description}
                </Typography>
              </CardContent>
            </Card>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default Dashboard; 