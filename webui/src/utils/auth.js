// Утилиты для работы с авторизацией

const TOKEN_KEY = 'access_token';
const USER_KEY = 'user_data';

export const authUtils = {
  // Сохранение токена и данных пользователя
  setAuth: (accessToken, userData) => {
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem(USER_KEY, JSON.stringify(userData));
  },

  // Получение токена
  getToken: () => {
    return localStorage.getItem(TOKEN_KEY);
  },

  // Получение данных пользователя
  getUser: () => {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  },

  // Проверка авторизации
  isAuthenticated: () => {
    return !!localStorage.getItem(TOKEN_KEY);
  },

  // Выход
  logout: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },

  // Обновление данных пользователя
  updateUser: (userData) => {
    localStorage.setItem(USER_KEY, JSON.stringify(userData));
  },
};



