import React, { useState, useEffect, useRef, useCallback } from 'react';
import { chatAPI } from '../api/chat';
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
      const chatExists = chats.some(chat => chat.id === chatId || chat.id === String(chatId));
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
  }, [chatId, chats, loadMessages]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadMessages = useCallback(async () => {
    if (!chatId) return;
    
    try {
      const loadedMessages = await chatAPI.getMessages(chatId);
      setMessages(loadedMessages);
    } catch (error) {
      console.error('Failed to load messages:', error);
      // В случае ошибки оставляем текущие сообщения
    }
  }, [chatId]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || loading || !chatId) return;

    const messageContent = inputValue.trim();
    setInputValue('');
    setLoading(true);

    // Оптимистично добавляем сообщение пользователя
    const userMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: messageContent,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      // Отправляем сообщение через API
      const response = await chatAPI.sendMessage(chatId, messageContent);
      
      // Обновляем временное сообщение пользователя
      if (response.message) {
        const updatedUserMessage = {
          id: response.message.id || userMessage.id,
          role: response.message.role || 'user',
          content: response.message.content || messageContent,
          timestamp: new Date(),
        };
        setMessages(prev => prev.map(msg => 
          msg.id === userMessage.id ? updatedUserMessage : msg
        ));
      }

      // Если это LLM чат, ответ должен прийти автоматически
      // Перезагружаем сообщения для получения ответа
      setTimeout(async () => {
        await loadMessages();
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Удаляем временное сообщение при ошибке
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
      alert('Не удалось отправить сообщение. Попробуйте еще раз.');
      setLoading(false);
    }
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

