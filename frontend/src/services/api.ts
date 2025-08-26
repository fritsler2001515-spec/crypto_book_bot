import axios from 'axios';
import { User, Portfolio, Transaction, AddCoinRequest, CoinData } from '../types';

// Определяем базовый URL для API
const isDevelopment = process.env.NODE_ENV === 'development';
const BACKEND_URL = isDevelopment 
  ? '' // В development используем прокси (пустая строка = тот же домен)
  : process.env.REACT_APP_API_URL || 'https://crypto-book-bot.onrender.com'; // В production - Render URL

const API_BASE_URL = BACKEND_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 секунд таймаут
});

// Добавляем перехватчик ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    if (error.code === 'ECONNREFUSED') {
      throw new Error('Сервер не отвечает. Убедитесь, что бэкенд запущен.');
    }
    if (error.response?.status === 404) {
      throw new Error('API endpoint не найден.');
    }
    throw error;
  }
);

export const apiService = {
  // Получить статус сервера
  getStatus: async () => {
    const response = await api.get('/status');
    return response.data;
  },

  // Получить пользователя
  getUser: async (telegramId: number): Promise<User> => {
    const response = await api.get(`/users/${telegramId}`);
    return response.data;
  },

  // Получить портфель
  getPortfolio: async (telegramId: number): Promise<Portfolio> => {
    const response = await api.get(`/portfolio/${telegramId}`);
    return response.data;
  },

  // Добавить монету
  addCoin: async (data: AddCoinRequest): Promise<Transaction> => {
    const response = await api.post('/portfolio/add-coin', data);
    return response.data;
  },

  // Получить транзакции
  getTransactions: async (telegramId: number): Promise<Transaction[]> => {
    const response = await api.get(`/transactions/${telegramId}`);
    return response.data;
  },

  // Получить топ монет
  getTopCoins: async (limit: number = 10): Promise<CoinData[]> => {
    const response = await api.get(`/market/top-coins?limit=${limit}`);
    return response.data;
  },

  // Получить лидеров роста
  getGrowthLeaders: async (limit: number = 5): Promise<CoinData[]> => {
    const response = await api.get(`/market/growth-leaders?limit=${limit}`);
    return response.data;
  },
}; 