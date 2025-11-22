import React, { useState, useEffect, useRef } from 'react';
import '../styles/ChatInterface.css';

function ChatInterface({ chatId, user, chats, onChatNotFound }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatNotFound, setChatNotFound] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Проверяем доступ к чату
    if (chats && chats.length > 0) {
      const chatExists = chats.some(chat => chat.id === chatId);
      if (!chatExists) {
        setChatNotFound(true);
        return;
      }
    }
    setChatNotFound(false);
    loadMessages();
    // Устанавливаем интервал для обновления сообщений каждые 5 секунд
    const interval = setInterval(loadMessages, 5000);
    return () => clearInterval(interval);
  }, [chatId, chats]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadMessages = async () => {
    // TODO: Заменить на реальный API
    // Пока используем моковые данные
    if (chatId) {
      const mockMessages = [
        { id: '1', role: 'user', content: 'Привет!', timestamp: new Date() },
        { id: '2', role: 'assistant', content: 'Здравствуйте! Чем могу помочь?', timestamp: new Date() },
      ];
      setMessages(mockMessages);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || loading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);
    setInputValue('');
    setLoading(true);

    // TODO: Отправить сообщение через API
    // Пока симулируем ответ
    setTimeout(() => {
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Это демо-ответ. В реальной версии здесь будет ответ от AI.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
      setLoading(false);
    }, 1000);
  };

  if (chatNotFound) {
    return (
      <div className="chat-interface">
        <div className="chat-error">
          <h2>404</h2>
          <p>Чат не найден или у вас нет доступа к этому чату</p>
          {onChatNotFound && (
            <button onClick={onChatNotFound} className="back-button">
              Вернуться на главную
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <p>Начните диалог, отправив сообщение</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
            >
              <div className="message-content">{message.content}</div>
            </div>
          ))
        )}
        {loading && (
          <div className="message assistant-message">
            <div className="message-content typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSend} className="chat-input-form">
        <div className="chat-input-container">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend(e);
              }
            }}
            placeholder="Введите сообщение..."
            rows={1}
            className="chat-input"
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || loading}
            className="send-button"
          >
            Отправить
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChatInterface;

