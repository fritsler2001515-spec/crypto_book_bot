import React, { useEffect, useState } from 'react';

declare global {
  interface Window {
    Telegram?: {
      WebApp: any;
    };
    TelegramGameProxy?: any; // Добавляем для совместимости
  }
}

interface TelegramWebAppContextType {
  webApp: any;
  isTelegramWebApp: boolean;
}

const TelegramWebAppContext = React.createContext<TelegramWebAppContextType>({
  webApp: null,
  isTelegramWebApp: false,
});

export const useTelegramWebApp = () => React.useContext(TelegramWebAppContext);

export const TelegramWebAppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [webApp, setWebApp] = useState<any>(null);
  const [isTelegramWebApp, setIsTelegramWebApp] = useState(false);

  useEffect(() => {
    try {
      // Предотвращаем ошибки TelegramGameProxy
      if (!window.TelegramGameProxy) {
        window.TelegramGameProxy = {
          receiveEvent: () => {},
          receiveError: () => {},
        };
      }
      
      // Проверяем, запущено ли приложение в Telegram Web App
      if (window.Telegram?.WebApp) {
        const tg = window.Telegram.WebApp;
        
        // Инициализируем Web App
        tg.ready();
        
        // Расширяем на весь экран
        tg.expand();
        
        // Настраиваем тему
        if (tg.colorScheme === 'dark') {
          document.body.classList.add('telegram-dark');
        }
        
        // Настраиваем основной цвет
        tg.setHeaderColor('#00d4aa');
        tg.setBackgroundColor('#0f1419');
        
        setWebApp(tg);
        setIsTelegramWebApp(true);
        
        console.log('Telegram Web App инициализирован');
      } else {
        console.log('Приложение запущено не в Telegram Web App');
      }
    } catch (error) {
      console.error('Ошибка при инициализации Telegram Web App:', error);
    }
  }, []);

  return (
    <TelegramWebAppContext.Provider value={{ webApp, isTelegramWebApp }}>
      {children}
    </TelegramWebAppContext.Provider>
  );
}; 