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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
} from '@mui/material';
import { 
  Receipt as ReceiptIcon, 
  ShoppingCart, 
  Sell,
  ExpandMore,
  ExpandLess,
  AccessTime,
  AttachMoney,
  FilterList,
  Clear
} from '@mui/icons-material';
import { apiService } from '../services/api';
import { Transaction, TransactionType } from '../types';

const Transactions: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set());
  
  // Состояние фильтров
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [dateFromFilter, setDateFromFilter] = useState<string>('');
  const [dateToFilter, setDateToFilter] = useState<string>('');
  const [filtersExpanded, setFiltersExpanded] = useState(false);

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

  // Фильтрация транзакций
  const filteredTransactions = transactions.filter(transaction => {
    // Фильтр по типу
    if (typeFilter !== 'all' && transaction.transaction_type !== typeFilter) {
      return false;
    }
    
    // Фильтр по дате
    if (dateFromFilter || dateToFilter) {
      const transactionDate = transaction.timestamp ? new Date(transaction.timestamp) : new Date();
      
      if (dateFromFilter) {
        const fromDate = new Date(dateFromFilter);
        if (transactionDate < fromDate) {
          return false;
        }
      }
      
      if (dateToFilter) {
        const toDate = new Date(dateToFilter);
        toDate.setHours(23, 59, 59, 999); // Конец дня
        if (transactionDate > toDate) {
          return false;
        }
      }
    }
    
    return true;
  });

  const clearFilters = () => {
    setTypeFilter('all');
    setDateFromFilter('');
    setDateToFilter('');
  };

  const hasActiveFilters = typeFilter !== 'all' || dateFromFilter || dateToFilter;

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

      {/* Панель фильтров */}
      <Card sx={{ 
        bgcolor: '#1a252f !important',
        mb: 3,
        borderRadius: 3,
        overflow: 'hidden',
        border: 'none !important',
        boxShadow: 'none !important',
        '& .MuiCardContent-root': {
          backgroundColor: '#1a252f !important',
          border: 'none !important'
        }
      }}>
        <CardContent sx={{ pb: filtersExpanded ? 3 : 2 }}>
          {/* Заголовок фильтров с кнопкой раскрытия */}
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              cursor: 'pointer'
            }}
            onClick={() => setFiltersExpanded(!filtersExpanded)}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <FilterList color="primary" />
              <Typography variant="h6">
                Фильтры
              </Typography>
              {hasActiveFilters && (
                <Chip
                  label={`${filteredTransactions.length}/${transactions.length}`}
                  color="primary"
                  size="small"
                  variant="outlined"
                />
              )}
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {hasActiveFilters && (
                <Button
                  size="small"
                  startIcon={<Clear />}
                  onClick={(e) => {
                    e.stopPropagation();
                    clearFilters();
                  }}
                  color="secondary"
                >
                  Очистить
                </Button>
              )}
              <IconButton size="small">
                {filtersExpanded ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            </Box>
          </Box>
          
          {/* Раскрываемая часть с фильтрами */}
          <Collapse in={filtersExpanded}>
            <Box sx={{ mt: 3 }}>
              <Box sx={{ 
                display: 'flex', 
                flexWrap: 'wrap', 
                gap: 2,
                alignItems: 'flex-end'
              }}>
                {/* Фильтр по типу */}
                <FormControl size="small" sx={{ minWidth: 140 }}>
                  <InputLabel>Тип операции</InputLabel>
                  <Select
                    value={typeFilter}
                    label="Тип операции"
                    onChange={(e) => setTypeFilter(e.target.value)}
                  >
                    <MenuItem value="all">Все</MenuItem>
                    <MenuItem value={TransactionType.BUY}>Покупки</MenuItem>
                    <MenuItem value={TransactionType.SELL}>Продажи</MenuItem>
                  </Select>
                </FormControl>

                {/* Фильтр по дате от */}
                <TextField
                  size="small"
                  label="Дата от"
                  type="date"
                  value={dateFromFilter}
                  onChange={(e) => setDateFromFilter(e.target.value)}
                  InputLabelProps={{
                    shrink: true,
                  }}
                  sx={{ minWidth: 140 }}
                />

                {/* Фильтр по дате до */}
                <TextField
                  size="small"
                  label="Дата до"
                  type="date"
                  value={dateToFilter}
                  onChange={(e) => setDateToFilter(e.target.value)}
                  InputLabelProps={{
                    shrink: true,
                  }}
                  sx={{ minWidth: 140 }}
                />
              </Box>
              
              {/* Показать количество отфильтрованных транзакций */}
              {hasActiveFilters && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="textSecondary">
                    Показано: {filteredTransactions.length} из {transactions.length} транзакций
                  </Typography>
                </Box>
              )}
            </Box>
          </Collapse>
        </CardContent>
      </Card>

      {/* Статистика */}
      <Box sx={{ mb: 4 }}>
        <Card sx={{ 
          bgcolor: '#1a252f !important',
          borderRadius: 3,
          overflow: 'hidden',
          border: 'none !important',
          boxShadow: 'none !important',
          '& .MuiCardContent-root': {
            backgroundColor: '#1a252f !important',
            border: 'none !important'
          }
        }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  Общая статистика
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {hasActiveFilters ? `Показано: ${filteredTransactions.length} из ${transactions.length}` : `Всего транзакций: ${transactions.length}`}
                </Typography>
              </Box>
              <Box textAlign="right">
                <Typography variant="h6" color="white">
                  ${filteredTransactions.reduce((sum, tx) => sum + (Number(tx.total_spent) || 0), 0).toFixed(2)}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {hasActiveFilters ? 'Сумма отфильтрованных' : 'Общая сумма'}
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
        ) : filteredTransactions.length === 0 ? (
          <Card sx={{ bgcolor: 'background.paper' }}>
            <CardContent>
              <Box textAlign="center" py={4}>
                <FilterList sx={{ fontSize: 60, color: 'textSecondary', mb: 2 }} />
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  Нет транзакций по выбранным фильтрам
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Попробуйте изменить критерии фильтрации
                </Typography>
              </Box>
            </CardContent>
          </Card>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {filteredTransactions.map((transaction, index) => {
              const isExpanded = expandedCards.has(transaction.id || index);
              const totalAmount = Number(transaction.total_spent) || Number(transaction.quantity) * Number(transaction.price);

              return (
                <Card 
                  key={transaction.id || index}
                  sx={{ 
                    bgcolor: '#1a252f !important',
        border: 'none !important',
        boxShadow: 'none !important',
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
                        gridTemplateColumns: { xs: 'repeat(1, 1fr)', sm: 'repeat(2, 1fr)' }, 
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