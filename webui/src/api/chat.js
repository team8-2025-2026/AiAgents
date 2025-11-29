// API клиент для работы с чатами
// Использует chatapi (отдельный сервис)

const CHAT_API_URL = import.meta.env.VITE_CHAT_API_URL || import.meta.env.VITE_API_URL || 'http://localhost:8001';

async function apiRequest(endpoint, options = {}) {
  const url = `${CHAT_API_URL}${endpoint}`;
  const token = localStorage.getItem('access_token');
  
  // Новый API использует access_token в query параметрах
  const urlObj = new URL(url);
  if (token) {
    urlObj.searchParams.append('access_token', token);
  }
  
  const response = await fetch(urlObj.toString(), {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: `HTTP error! status: ${response.status}` }));
    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

export const chatAPI = {
  // Получить список чатов
  getChats: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      // Фильтры пока не поддерживаются в новом API, но оставляем для совместимости
      const endpoint = `/chats${params.toString() ? `?${params.toString()}` : ''}`;
      const response = await apiRequest(endpoint);
      
      if (response.success && response.data) {
        return response.data;
      }
      if (Array.isArray(response)) {
        return response;
      }
      return [];
    } catch (error) {
      console.error('Error loading chats:', error);
      return [];
    }
  },

  // Создать новый чат
  createChat: async (title = 'Новый чат') => {
    try {
      // Новый API не принимает title при создании, создается с дефолтным названием
      const response = await apiRequest('/chat', {
        method: 'PUT',
      });
      
      if (response.success && response.data) {
        return response.data;
      }
      return response;
    } catch (error) {
      console.error('Error creating chat:', error);
      throw error;
    }
  },

  // Получить информацию о чате
  getChat: async (chatId) => {
    try {
      // Новый API использует query параметр id
      const response = await apiRequest(`/chat?id=${chatId}`);
      
      if (response.success && response.data) {
        return response.data;
      }
      return response;
    } catch (error) {
      console.error('Error loading chat:', error);
      throw error;
    }
  },

  // Обновить чат (переименование)
  updateChat: async (chatId, updates) => {
    try {
      // Новый API использует query параметры: id, title, access_token
      const title = updates.title || updates.student_title || updates.assistent_title;
      const response = await apiRequest(`/chat?id=${chatId}&title=${encodeURIComponent(title)}`, {
        method: 'PATCH',
      });
      
      if (response.success && response.data) {
        return response.data;
      }
      return response;
    } catch (error) {
      console.error('Error updating chat:', error);
      throw error;
    }
  },

  // Удалить чат
  deleteChat: async (chatId) => {
    try {
      // Новый API использует query параметры: id, access_token
      const response = await apiRequest(`/chat?id=${chatId}`, {
        method: 'DELETE',
      });
      
      if (response.success && response.data) {
        return response.data;
      }
      return response;
    } catch (error) {
      console.error('Error deleting chat:', error);
      throw error;
    }
  },

  // Получить сообщения чата
  getMessages: async (chatId) => {
    try {
      // Новый API: GET /chat/history?id=...&access_token=...
      const response = await apiRequest(`/chat/history?id=${chatId}`);
      
      if (response.success && response.data) {
        // Преобразуем формат сообщений
        return response.data.map(msg => {
          // Определяем роль: LLM всегда assistant, HUMAN с status STUDENT - user, остальные - assistant
          let role = 'assistant';
          if (msg.author?.type === 'LLM') {
            role = 'assistant';
          } else if (msg.author?.type === 'HUMAN' && msg.author?.data?.status === 'STUDENT') {
            role = 'user';
          } else {
            role = 'assistant';
          }
          
          return {
            id: msg.id,
            role: role,
            content: msg.text,
            timestamp: new Date(),
          };
        });
      }
      if (Array.isArray(response)) {
        return response;
      }
      return [];
    } catch (error) {
      console.error('Error loading messages:', error);
      return [];
    }
  },

  // Отправить сообщение
  sendMessage: async (chatId, content) => {
    try {
      // Новый API: POST /chat/send_message?id=...&text=...&access_token=...
      const response = await apiRequest(`/chat/send_message?id=${chatId}&text=${encodeURIComponent(content)}`, {
        method: 'POST',
      });
      
      if (response.success && response.data) {
        // Преобразуем формат ответа
        const message = response.data;
        // Определяем роль: LLM всегда assistant, HUMAN с status STUDENT - user, остальные - assistant
        let role = 'assistant';
        if (message.author?.type === 'LLM') {
          role = 'assistant';
        } else if (message.author?.type === 'HUMAN' && message.author?.data?.status === 'STUDENT') {
          role = 'user';
        } else {
          role = 'assistant';
        }
        
        return {
          message: {
            id: message.id,
            content: message.text,
            role: role,
          },
        };
      }
      return response;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },
};
