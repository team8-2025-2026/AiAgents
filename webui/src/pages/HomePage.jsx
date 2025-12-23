import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authUtils } from '../utils/auth';
import { chatAPI } from '../api/chat';
import ChatInterface from '../components/ChatInterface';
import ChatList from '../components/ChatList';
import Header from '../components/Header';
import '../styles/HomePage.css';

function HomePage() {
  const [chats, setChats] = useState([]);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [filters, setFilters] = useState({ status: null, studentId: null });
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const user = authUtils.getUser();
  const chatsUpdateIntervalRef = useRef(null);
  const filtersDebounceRef = useRef(null);
  const lastChatsHashRef = useRef(null);

  // Функция для вычисления хеша списка чатов (для оптимизации обновлений)
  const getChatsHash = useCallback((chatsList) => {
    return chatsList.map(c => `${c.id}:${c.title}`).join('|');
  }, []);

  const loadChats = useCallback(async () => {
    try {
      const loadedChats = await chatAPI.getChats();
      // Преобразуем формат данных под наш UI
      const formattedChats = loadedChats.map(chat => ({
        id: chat.id,
        title: chat.title || chat.student_title || chat.assistent_title || 'Без названия',
        student_id: chat.student?.id || null,
        status: 'open', // Новый API не возвращает status, используем дефолт
        last_message: '',
      }));
      
      // Проверяем, действительно ли список изменился
      const newHash = getChatsHash(formattedChats);
      if (lastChatsHashRef.current !== newHash) {
        lastChatsHashRef.current = newHash;
        setChats(prevChats => {
          // Дополнительная проверка: обновляем только если действительно есть изменения
          const prevHash = getChatsHash(prevChats);
          if (prevHash !== newHash) {
            return formattedChats;
          }
          return prevChats;
        });
      }
      
      return formattedChats;
    } catch (error) {
      console.error('Failed to load chats:', error);
      // Не обновляем состояние при ошибке, чтобы не вызывать мерцание
      return [];
    }
  }, [getChatsHash]);

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }

    // Загружаем чаты при монтировании
    loadChats();

    // Проверяем chat_id в URL
    const chatId = searchParams.get('chat');
    if (chatId) {
      setSelectedChatId(chatId);
    }

    // Для учителей: периодическое обновление списка чатов (чтобы видеть новые эскалированные чаты)
    if (user.status === 'ASSISTENT') {
      chatsUpdateIntervalRef.current = setInterval(() => {
        loadChats();
      }, 10000); // Обновляем каждые 10 секунд (уменьшено для предотвращения мерцания)
    }

    return () => {
      if (chatsUpdateIntervalRef.current) {
        clearInterval(chatsUpdateIntervalRef.current);
        chatsUpdateIntervalRef.current = null;
      }
      if (filtersDebounceRef.current) {
        clearTimeout(filtersDebounceRef.current);
        filtersDebounceRef.current = null;
      }
    };
  }, [user, navigate, searchParams, loadChats]);

  // Дебаунсинг для фильтров (для учителей)
  useEffect(() => {
    if (user && user.status === 'ASSISTENT') {
      // Очищаем предыдущий таймер
      if (filtersDebounceRef.current) {
        clearTimeout(filtersDebounceRef.current);
      }
      
      // Устанавливаем новый таймер с задержкой 500ms
      filtersDebounceRef.current = setTimeout(() => {
        loadChats();
      }, 500);
    }
  }, [filters, user, loadChats]);

  const handleChatSelect = (chatId) => {
    setSelectedChatId(chatId);
    setSearchParams({ chat: chatId });
  };

  const handleNewChat = async () => {
    if (user.status === 'STUDENT') {
      try {
        const newChat = await chatAPI.createChat();
        console.log('Created chat:', newChat);
        
        // Безопасное форматирование данных чата
        const formattedChat = {
          id: newChat?.id || null,
          title: newChat?.title || newChat?.student_title || newChat?.assistent_title || 'Новый чат',
          student_id: newChat?.student?.id || (typeof newChat?.student === 'object' && newChat?.student ? newChat.student.id : null) || null,
          status: 'open',
          last_message: '',
        };
        
        if (!formattedChat.id) {
          throw new Error('Не удалось получить ID созданного чата');
        }
        
        setChats([formattedChat, ...chats]);
        // Небольшая задержка перед выбором чата, чтобы состояние обновилось
        setTimeout(() => {
          handleChatSelect(formattedChat.id);
        }, 100);
      } catch (error) {
        console.error('Failed to create chat:', error);
        const errorMessage = error.message || 'Не удалось создать чат. Попробуйте еще раз.';
        alert(errorMessage);
      }
    } else {
      alert('Только студенты могут создавать чаты');
    }
  };

  const handleChatDelete = async (chatId) => {
    if (user.status === 'STUDENT') {
      try {
        await chatAPI.deleteChat(chatId);
        setChats(chats.filter(chat => chat.id !== chatId));
        if (selectedChatId === chatId) {
          setSelectedChatId(null);
          setSearchParams({});
        }
      } catch (error) {
        console.error('Failed to delete chat:', error);
        alert('Не удалось удалить чат. Попробуйте еще раз.');
      }
    }
  };

  const handleChatRename = async (chatId, newTitle) => {
    try {
      const updatedChat = await chatAPI.updateChat(chatId, { title: newTitle });
      const formattedChat = {
        id: updatedChat.id,
        title: updatedChat.title || updatedChat.student_title || updatedChat.assistent_title || newTitle,
        student_id: updatedChat.student?.id || null,
        status: 'open',
        last_message: '',
      };
      setChats(chats.map(chat =>
        chat.id === chatId ? formattedChat : chat
      ));
    } catch (error) {
      console.error('Failed to rename chat:', error);
      alert('Не удалось переименовать чат. Попробуйте еще раз.');
    }
  };

  if (!user) {
    return (
      <div className="home-page">
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <p>Загрузка...</p>
        </div>
      </div>
    );
  }

  try {
    return (
      <div className="home-page">
        <div className="sidebar">
          <ChatList
            chats={chats}
            selectedChatId={selectedChatId}
            onChatSelect={handleChatSelect}
            onNewChat={user.status === 'STUDENT' ? handleNewChat : null}
            onChatDelete={user.status === 'STUDENT' ? handleChatDelete : null}
            onChatRename={handleChatRename}
            userStatus={user.status}
            filters={user.status === 'ASSISTENT' ? filters : null}
            onFiltersChange={user.status === 'ASSISTENT' ? setFilters : null}
          />
        </div>
        <div className="main-content">
          <Header user={user} />
          <div className="chat-container">
            {selectedChatId ? (
              <ChatInterface
                chatId={selectedChatId}
                user={user}
                chats={chats}
                onChatNotFound={() => {
                  setSelectedChatId(null);
                  setSearchParams({});
                }}
              />
            ) : (
              <div className="welcome-screen">
                <h1>Добро пожаловать, {user.first_name}!</h1>
                <p>Выберите чат из списка слева или создайте новый</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  } catch (error) {
    console.error('Error rendering HomePage:', error);
    return (
      <div className="home-page">
        <div style={{ padding: '20px', textAlign: 'center', color: 'white' }}>
          <h2>Произошла ошибка</h2>
          <p>{error.message}</p>
          <button onClick={() => window.location.reload()}>Перезагрузить страницу</button>
        </div>
      </div>
    );
  }
}

export default HomePage;

