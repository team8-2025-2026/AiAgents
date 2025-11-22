import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authUtils } from '../utils/auth';
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
  }, [user, navigate, searchParams]);

  const loadChats = async () => {
    // TODO: Заменить на реальный API
    // Пока используем моковые данные
    const mockChats = [
      { id: '1', title: 'Новый чат', student_id: null, status: 'open', last_message: 'Привет!' },
      { id: '2', title: 'Вопрос по математике', student_id: '1', status: 'open', last_message: 'Как решить это уравнение?' },
    ];
    setChats(mockChats);
    return mockChats;
  };

  const handleChatSelect = (chatId) => {
    setSelectedChatId(chatId);
    setSearchParams({ chat: chatId });
  };

  const handleNewChat = async () => {
    if (user.status === 'STUDENT') {
      // TODO: Создать новый чат через API
      const newChatId = Date.now().toString();
      const newChat = {
        id: newChatId,
        title: 'Новый чат',
        student_id: null,
        status: 'open',
        last_message: '',
      };
      setChats([newChat, ...chats]);
      handleChatSelect(newChatId);
    }
  };

  const handleChatDelete = async (chatId) => {
    if (user.status === 'STUDENT') {
      // TODO: Удалить чат через API
      setChats(chats.filter(chat => chat.id !== chatId));
      if (selectedChatId === chatId) {
        setSelectedChatId(null);
        setSearchParams({});
      }
    }
  };

  const handleChatRename = async (chatId, newTitle) => {
    // TODO: Обновить название чата через API
    setChats(chats.map(chat =>
      chat.id === chatId ? { ...chat, title: newTitle } : chat
    ));
  };

  if (!user) {
    return null;
  }

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
          filters={user.status === 'TEACHER' ? filters : null}
          onFiltersChange={user.status === 'TEACHER' ? setFilters : null}
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
}

export default HomePage;

