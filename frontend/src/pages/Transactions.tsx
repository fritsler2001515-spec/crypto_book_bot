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
  Grid,
} from '@mui/material';
import { 
  Receipt as ReceiptIcon, 
  ShoppingCart, 
  Sell,
  ExpandMore,
  ExpandLess,
  AccessTime,
  AttachMoney
} from '@mui/icons-material';
import { apiService } from '../services/api';
import { Transaction, TransactionType } from '../types';

const Transactions: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set());

  // Для демонстрации используем тестовый Telegram ID
  const testTelegramId = 1042267533;

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setLoading(true);
        const data = await apiService.getTransactions(testTelegramId);
        setTransactions(data);
      } catch (err) {
        setError('Ошибка при загрузке транзакций');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const totalSpent = transactions.reduce((sum, tx) => sum + (Number(tx.total_spent) || 0), 0);

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
        📋 Транзакции
      </Typography>

      {/* Статистика */}
      <Box sx={{ mb: 4 }}>
        <Card sx={{ bgcolor: 'background.paper' }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  Общая статистика
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Всего транзакций: {transactions.length}
                </Typography>
              </Box>
              <Box textAlign="right">
                <Typography variant="h6" color="primary.main">
                  ${totalSpent.toFixed(2)}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Общая сумма
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Транзакции в виде карточек */}
      <Box>
        <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
          История транзакций
        </Typography>
        
        {transactions.length === 0 ? (
          <Card sx={{ bgcolor: 'background.paper' }}>
            <CardContent>
              <Box textAlign="center" py={4}>
                <ReceiptIcon sx={{ fontSize: 60, color: 'textSecondary', mb: 2 }} />
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  Транзакций пока нет
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Добавьте первую монету в портфель
                </Typography>
              </Box>
            </CardContent>
          </Card>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {transactions.map((transaction, index) => {
              const isExpanded = expandedCards.has(transaction.id || index);
              const totalAmount = Number(transaction.total_spent) || Number(transaction.quantity) * Number(transaction.price);

              return (
                <Card 
                  key={transaction.id || index}
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
                    onClick={() => toggleCardExpansion(transaction.id || index)}
                  >
                    {/* Основная информация - всегда видна */}
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: isExpanded ? 2 : 0 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        {/* Иконка типа транзакции */}
                        <Box sx={{
                          width: 48,
                          height: 48,
                          borderRadius: '50%',
                          bgcolor: transaction.transaction_type === TransactionType.BUY ? 'success.main' : 'error.main',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white'
                        }}>
                          {transaction.transaction_type === TransactionType.BUY ? <ShoppingCart /> : <Sell />}
                        </Box>
                        
                        <Box>
                          <Typography variant="h6" fontWeight="bold">
                            {transaction.symbol}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {transaction.name}
                          </Typography>
                          <Chip
                            label={transaction.transaction_type === TransactionType.BUY ? 'Покупка' : 'Продажа'}
                            color={transaction.transaction_type === TransactionType.BUY ? 'success' : 'error'}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      </Box>

                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        {/* Сумма и дата */}
                        <Box sx={{ textAlign: 'right' }}>
                          <Typography
                            variant="h6"
                            color={transaction.transaction_type === TransactionType.BUY ? 'error.main' : 'success.main'}
                            fontWeight="bold"
                          >
                            {transaction.transaction_type === TransactionType.BUY ? '-' : '+'}${totalAmount.toFixed(2)}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {transaction.timestamp ? formatDate(transaction.timestamp).split(',')[0] : 'Сегодня'}
                          </Typography>
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
                            {Number(transaction.quantity).toFixed(4)} {transaction.symbol}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            Цена за единицу
                          </Typography>
                          <Typography variant="body1" fontWeight="medium">
                            ${Number(transaction.price).toFixed(2)}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            Общая сумма
                          </Typography>
                          <Typography 
                            variant="body1" 
                            fontWeight="medium"
                            color={transaction.transaction_type === TransactionType.BUY ? 'error.main' : 'success.main'}
                          >
                            {transaction.transaction_type === TransactionType.BUY ? '-' : '+'}${totalAmount.toFixed(2)}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            Дата и время
                          </Typography>
                          <Typography variant="body1" fontWeight="medium">
                            {transaction.timestamp ? formatDate(transaction.timestamp) : 'Сегодня'}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            ID транзакции
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            #{transaction.id || 'N/A'}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            Статус
                          </Typography>
                          <Chip
                            label="Завершена"
                            color="success"
                            size="small"
                            variant="outlined"
                          />
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

export default Transactions; 