const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

export const authAPI = {
  // Авторизация по email и паролю
  login: async (email, password) => {
    const params = new URLSearchParams({ email, password });
    return apiRequest(`/user?${params.toString()}`);
  },

  // Получение пользователя по токену
  getUserByToken: async (accessToken) => {
    const params = new URLSearchParams({ access_token: accessToken });
    return apiRequest(`/user/by_token?${params.toString()}`);
  },

  // Создание пользователя (только для ассистентов)
  createUser: async (email, first_name, last_name, status, accessToken) => {
    const params = new URLSearchParams({
      email,
      first_name,
      last_name,
      status,
      access_token: accessToken,
    });
    return apiRequest(`/user?${params.toString()}`, {
      method: 'PUT',
    });
  },

  // Обновление пользователя
  updateUser: async (email, accessToken, updates) => {
    const params = new URLSearchParams({
      email,
      access_token: accessToken,
    });
    
    // Добавляем только непустые поля
    Object.keys(updates).forEach(key => {
      if (updates[key] !== null && updates[key] !== undefined && updates[key] !== '') {
        params.append(key, updates[key]);
      }
    });
    
    return apiRequest(`/user?${params.toString()}`, {
      method: 'PATCH',
    });
  },

  // Удаление пользователя
  deleteUser: async (email, accessToken) => {
    const params = new URLSearchParams({
      email,
      access_token: accessToken,
    });
    return apiRequest(`/user?${params.toString()}`, {
      method: 'DELETE',
    });
  },
};

