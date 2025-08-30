export interface User {
  id: number;
  telegram_id: number;
  balance: number;
}

export interface PortfolioItem {
  id: number;
  user_id: number;
  symbol: string;
  name: string;
  total_quantity: number;
  avg_price: number;
  current_price: number;
  total_spent: number;
  last_updated: string;
}

export interface Portfolio {
  telegram_id: number;
  portfolio: PortfolioItem[];
}

export enum TransactionType {
  BUY = "buy",
  SELL = "sell"
}

export interface Transaction {
  id?: number;
  symbol: string;
  name: string;
  quantity: number;
  price: number;
  total_spent?: number;
  transaction_type: TransactionType;
  timestamp?: string;
  total_amount?: number;
}

export interface AddCoinRequest {
  telegram_id: number;
  symbol: string;
  name: string;
  quantity: number;
  price: number;
}

export interface SellCoinRequest {
  telegram_id: number;
  symbol: string;
  quantity: number;
  price: number;
}

export interface CoinData {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  market_cap?: number;
  market_cap_rank?: number;
  price_change_percentage_24h?: number;
  image?: string;
  total_volume?: number;
} 