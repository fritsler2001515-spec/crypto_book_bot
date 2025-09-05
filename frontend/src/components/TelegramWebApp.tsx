import React from 'react';
import {
  Box,
  Container,
  Paper,
  Button,
  Typography,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  AccountBalance as PortfolioIcon,
  Add as AddIcon,
  Receipt as TransactionsIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTelegramWebApp } from './TelegramWebAppProvider';

const TelegramWebApp: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isTelegramWebApp } = useTelegramWebApp();

  const navItems = [
    { path: '/', label: 'Дашборд', icon: <DashboardIcon /> },
    { path: '/portfolio', label: 'Портфель', icon: <PortfolioIcon /> },
    { path: '/add-coin', label: 'Добавить', icon: <AddIcon /> },
    { path: '/transactions', label: 'Транзакции', icon: <TransactionsIcon /> },
  ];

  return (
    <Box 
      className={isTelegramWebApp ? 'telegram-webapp' : ''}
      sx={{ 
        minHeight: '100vh', 
        bgcolor: 'background.default',
        display: 'flex',
        flexDirection: 'column',
        pb: isTelegramWebApp ? 8 : 0 // Отступ для кнопок внизу только в Telegram
      }}>
      {/* Основной контент */}
      <Container maxWidth="lg" sx={{ py: 2, flex: 1 }}>
        {children}
      </Container>

      {/* Навигационные кнопки внизу - только в Telegram Web App */}
      {isTelegramWebApp && (
        <Paper
          elevation={8}
          sx={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            bgcolor: '#1565c0', // Темно-синий фон
            borderTop: '1px solid',
            borderColor: 'divider',
            zIndex: 1000,
          }}
        >
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-around',
            alignItems: 'center',
            py: 1,
          }}
        >
          {navItems.map((item) => (
            <Button
              key={item.path}
              onClick={() => navigate(item.path)}
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                minWidth: 'auto',
                px: 1,
                py: 1,
                color: location.pathname === item.path ? '#ffffff' : 'rgba(255, 255, 255, 0.7)',
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 0.1)',
                  color: '#ffffff',
                },
              }}
            >
              <Box sx={{ mb: 0.5 }}>
                {React.cloneElement(item.icon, {
                  sx: { fontSize: 20 }
                })}
              </Box>
              <Typography variant="caption" sx={{ fontSize: '0.7rem' }}>
                {item.label}
              </Typography>
            </Button>
          ))}
        </Box>
        </Paper>
      )}
    </Box>
  );
};

export default TelegramWebApp; 