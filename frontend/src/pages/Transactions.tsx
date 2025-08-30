import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
} from '@mui/material';
import { Receipt as ReceiptIcon, ShoppingCart, Sell } from '@mui/icons-material';
import { apiService } from '../services/api';
import { Transaction, TransactionType } from '../types';

const Transactions: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

      {/* Таблица транзакций */}
      <Card sx={{ bgcolor: 'background.paper' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
            История транзакций
          </Typography>
          
          {transactions.length === 0 ? (
            <Box textAlign="center" py={4}>
              <ReceiptIcon sx={{ fontSize: 60, color: 'textSecondary', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" gutterBottom>
                Транзакций пока нет
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
                    <TableCell align="center">Тип</TableCell>
                    <TableCell align="right">Количество</TableCell>
                    <TableCell align="right">Цена</TableCell>
                    <TableCell align="right">Общая сумма</TableCell>
                    <TableCell align="right">Дата</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {transactions.map((transaction, index) => (
                    <TableRow key={transaction.id || index}>
                      <TableCell>
                        <Box>
                          <Typography variant="subtitle1" fontWeight="bold">
                            {transaction.symbol}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {transaction.name}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={transaction.transaction_type === TransactionType.BUY ? 'Покупка' : 'Продажа'}
                          color={transaction.transaction_type === TransactionType.BUY ? 'success' : 'error'}
                          size="small"
                          icon={transaction.transaction_type === TransactionType.BUY ? <ShoppingCart /> : <Sell />}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body1">
                          {Number(transaction.quantity).toFixed(4)}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body1">
                          ${Number(transaction.price).toFixed(2)}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography 
                          variant="body1" 
                          fontWeight="bold"
                          color={transaction.transaction_type === TransactionType.BUY ? 'error.main' : 'success.main'}
                        >
                          {transaction.transaction_type === TransactionType.BUY ? '-' : '+'}${(Number(transaction.total_spent) || Number(transaction.quantity) * Number(transaction.price)).toFixed(2)}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="textSecondary">
                          {transaction.timestamp ? formatDate(transaction.timestamp) : 'Сегодня'}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Transactions; 