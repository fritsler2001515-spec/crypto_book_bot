import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import TelegramWebApp from './components/TelegramWebApp';
import { TelegramWebAppProvider } from './components/TelegramWebAppProvider';
import Dashboard from './pages/Dashboard';
import Portfolio from './pages/Portfolio';
import AddCoin from './pages/AddCoin';
import Transactions from './pages/Transactions';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2196f3', // Синий цвет вместо бирюзового
    },
    secondary: {
      main: '#ff6b35',
    },
    background: {
      default: '#0f1419',
      paper: '#1a2332',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <TelegramWebAppProvider>
        <Router>
          <TelegramWebApp>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/portfolio" element={<Portfolio />} />
              <Route path="/add-coin" element={<AddCoin />} />
              <Route path="/transactions" element={<Transactions />} />
            </Routes>
          </TelegramWebApp>
        </Router>
      </TelegramWebAppProvider>
    </ThemeProvider>
  );
}

export default App;
