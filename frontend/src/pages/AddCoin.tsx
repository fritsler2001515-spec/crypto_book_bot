import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { apiService } from '../services/api';
import { AddCoinRequest } from '../types';

const steps = ['Символ монеты', 'Название', 'Количество', 'Цена покупки'];

const AddCoin: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [formData, setFormData] = useState<AddCoinRequest>({
    telegram_id: 1042267533, // Тестовый ID
    symbol: '',
    name: '',
    quantity: 0,
    price: 0,
  });
  
  // Строковые значения для полей ввода чисел
  const [quantityInput, setQuantityInput] = useState('');
  const [priceInput, setPriceInput] = useState('');

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleInputChange = (field: keyof AddCoinRequest, value: string | number) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      await apiService.addCoin(formData);
      
      setSuccess('Монета успешно добавлена в портфель!');
      setFormData({
        telegram_id: 1042267533,
        symbol: '',
        name: '',
        quantity: 0,
        price: 0,
      });
      setQuantityInput('');
      setPriceInput('');
      setActiveStep(0);
    } catch (err) {
      setError('Ошибка при добавлении монеты');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const parseNumberInput = (input: string): number => {
    const cleaned = input.replace(',', '.');
    const parsed = parseFloat(cleaned);
    return isNaN(parsed) ? 0 : parsed;
  };

  const isStepValid = (step: number) => {
    switch (step) {
      case 0:
        return formData.symbol.trim().length > 0;
      case 1:
        return formData.name.trim().length > 0;
      case 2:
        return quantityInput.trim().length > 0 && parseNumberInput(quantityInput) > 0;
      case 3:
        return priceInput.trim().length > 0 && parseNumberInput(priceInput) > 0;
      default:
        return false;
    }
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <TextField
            fullWidth
            label="Символ монеты (например, BTC)"
            value={formData.symbol}
            onChange={(e) => handleInputChange('symbol', e.target.value.toUpperCase())}
            placeholder="BTC"
            helperText="Введите символ криптовалюты"
          />
        );
      case 1:
        return (
          <TextField
            fullWidth
            label="Название монеты"
            value={formData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            placeholder="Bitcoin"
            helperText="Введите полное название криптовалюты"
          />
        );
      case 2:
        return (
          <TextField
            fullWidth
            label="Количество монет"
            type="text"
            inputProps={{
              inputMode: "decimal"
            }}
            value={quantityInput}
            onChange={(e) => {
              const value = e.target.value;
              // Разрешаем только цифры, точку и запятую
              if (/^[0-9]*[.,]?[0-9]*$/.test(value) || value === '') {
                setQuantityInput(value);
                const numValue = parseNumberInput(value);
                handleInputChange('quantity', numValue);
              }
            }}
            placeholder="0.5"
            helperText="Введите количество купленных монет (можно с точкой или запятой)"
          />
        );
      case 3:
        return (
          <TextField
            fullWidth
            label="Цена покупки (USD)"
            type="text"
            inputProps={{
              inputMode: "decimal"
            }}
            value={priceInput}
            onChange={(e) => {
              const value = e.target.value;
              // Разрешаем только цифры, точку и запятую
              if (/^[0-9]*[.,]?[0-9]*$/.test(value) || value === '') {
                setPriceInput(value);
                const numValue = parseNumberInput(value);
                handleInputChange('price', numValue);
              }
            }}
            placeholder="50000.5"
            helperText="Введите цену за одну монету в долларах (можно с точкой или запятой)"
          />
        );
      default:
        return null;
    }
  };

  return (
    <Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Card sx={{ 
        bgcolor: '#1a252f !important',
        border: 'none !important',
        boxShadow: 'none !important',
        borderRadius: 3
      }}>
        <CardContent>
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          <Box sx={{ mt: 2, mb: 1 }}>
            {renderStepContent(activeStep)}
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
            <Button
              disabled={activeStep === 0}
              onClick={handleBack}
            >
              Назад
            </Button>
            <Box>
              {activeStep === steps.length - 1 ? (
                <Button
                  variant="contained"
                  onClick={handleSubmit}
                  disabled={loading || !isStepValid(activeStep)}
                  startIcon={loading ? <CircularProgress size={20} /> : <AddIcon />}
                >
                  {loading ? 'Добавление...' : 'Добавить монету'}
                </Button>
              ) : (
                <Button
                  variant="contained"
                  onClick={handleNext}
                  disabled={!isStepValid(activeStep)}
                >
                  Далее
                </Button>
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Предварительный просмотр */}
      {activeStep > 0 && (
        <Card sx={{ 
          bgcolor: '#1a252f !important',
          border: 'none !important',
          boxShadow: 'none !important',
          borderRadius: 3,
          mt: 3
        }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Предварительный просмотр
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              <Box sx={{ flex: '1 1 45%', minWidth: 200 }}>
                <Typography variant="body2" color="textSecondary">
                  Символ: {formData.symbol || '—'}
                </Typography>
              </Box>
              <Box sx={{ flex: '1 1 45%', minWidth: 200 }}>
                <Typography variant="body2" color="textSecondary">
                  Название: {formData.name || '—'}
                </Typography>
              </Box>
              <Box sx={{ flex: '1 1 45%', minWidth: 200 }}>
                <Typography variant="body2" color="textSecondary">
                  Количество: {quantityInput || '—'}
                </Typography>
              </Box>
              <Box sx={{ flex: '1 1 45%', minWidth: 200 }}>
                <Typography variant="body2" color="textSecondary">
                  Цена: ${priceInput || '—'}
                </Typography>
              </Box>
              {formData.quantity > 0 && formData.price > 0 && (
                <Box sx={{ flex: '1 1 100%' }}>
                  <Typography variant="body1" color="primary.main">
                    Общая сумма: ${(formData.quantity * formData.price).toFixed(2)}
                  </Typography>
                </Box>
              )}
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default AddCoin; 