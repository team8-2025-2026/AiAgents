import React, { useState, useEffect, useRef, useCallback } from 'react';
import { chatAPI } from '../api/chat';
import '../styles/ChatInterface.css';
import { use } from 'react';

function ChatInterface({ chatId, user, chats, onChatNotFound }) {
  const [messages, setMessages] = useState([]);
  const [chatData, setChatData] = useState(null);
  const [actions, setActions] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatNotFound, setChatNotFound] = useState(false);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const checkIntervalRef = useRef(null);

  useEffect(() => {
    if (!chatId) {
      return;
    }
    
    // Очищаем предыдущий интервал проверки ответа
    if (checkIntervalRef.current) {
      clearInterval(checkIntervalRef.current);
      checkIntervalRef.current = null;
    }
    
    // Сбрасываем состояние загрузки при смене чата
    setLoading(false);
    
    // Проверяем доступ к чату
    if (chats && chats.length > 0) {
      const chatExists = chats.some(chat => {
        const chatIdNum = typeof chat.id === 'number' ? chat.id : parseInt(chat.id);
        const selectedIdNum = typeof chatId === 'number' ? chatId : parseInt(chatId);
        return chatIdNum === selectedIdNum || chat.id === String(chatId) || String(chat.id) === String(chatId);
      });
      if (!chatExists) {
        setChatNotFound(true);
        return;
      }
    }
    setChatNotFound(false);
    updateLoop();
    // Устанавливаем интервал для обновления сообщений каждые 3 секунды (оптимизировано)
    const interval = setInterval(updateLoop, 3000);
    return () => {
      clearInterval(interval);
      if (checkIntervalRef.current) {
        clearInterval(checkIntervalRef.current);
        checkIntervalRef.current = null;
      }
      setLoading(false);
    };
  }, [chatId, chats]);

  useEffect(() => {
    scrollToBottom();
  }, [messagesEndRef]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const updateLoop = async () => {
    await updateChatData();
    await loadMessages();
  };

  const updateChatData = async () => {
    if (!chatId) return;
    
    try {
      const loadedChatData = await chatAPI.getChat(chatId);
      setChatData(loadedChatData);
    } catch (error) {
      console.error('Failed to load messages:', error);
      setChatData(null);
      return;
    }

    var newActions = [];
    console.log(chatData);
    if (chatData != null && chatData.assistent.type == "LLM") {
      newActions.push(
        {
          "key": "CallAssistantKeyProp",
          "title": "Позвать ассистента",
          "effect": async () => {
            const newChatData = await chatAPI.actions.callAssistant(chatId);
            setChatData(newChatData);
          },
        }
      );
    }

    setActions(newActions)
  };

  const loadMessages = async () => {
    if (!chatId) return;
    
    try {
      const loadedMessages = await chatAPI.getMessages(chatId);
      if (Array.isArray(loadedMessages)) {
        setMessages(loadedMessages);
        // Если загружаем сообщения и loading активен, но уже есть ответ от assistant,
        // значит ответ уже получен, останавливаем анимацию
        if (loading) {
          const hasAssistantMessage = loadedMessages.some(msg => msg.role === 'assistant');
          if (hasAssistantMessage) {
            setLoading(false);
            if (checkIntervalRef.current) {
              clearInterval(checkIntervalRef.current);
              checkIntervalRef.current = null;
            }
          }
        }
      } else {
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
      // В случае ошибки оставляем пустой массив для нового чата
      setMessages([]);
    }
  };

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
      // Перезагружаем сообщения для получения ответа с задержкой
      // Сначала показываем анимацию "мышления", потом проверяем ответ
      const messageIdsBefore = new Set(messages.map(m => m.id));
      let responseReceived = false; // Флаг для отслеживания получения ответа
      
      setTimeout(async () => {
        // Проверяем, появился ли новый ответ от LLM
        const checkForResponse = async () => {
          if (responseReceived) {
            return true; // Ответ уже получен, не проверяем дальше
          }
          
          try {
            const currentMessages = await chatAPI.getMessages(chatId);
            if (Array.isArray(currentMessages)) {
              // Проверяем, есть ли новое сообщение от assistant (LLM)
              const hasNewAssistantMessage = currentMessages.some(msg => 
                msg.role === 'assistant' && !messageIdsBefore.has(msg.id)
              );
              
              if (hasNewAssistantMessage) {
                // Ответ получен, обновляем сообщения и останавливаем анимацию
                responseReceived = true;
                setMessages(currentMessages);
                setLoading(false);
                if (checkIntervalRef.current) {
                  clearInterval(checkIntervalRef.current);
                  checkIntervalRef.current = null;
                }
                return true; // Ответ получен
              }
              
              // Обновляем сообщения на всякий случай
              setMessages(currentMessages);
            }
          } catch (error) {
            console.error('Error checking for response:', error);
          }
          return false; // Ответ еще не получен
        };
        
        // Проверяем ответ каждые 1.5 секунды, максимум 15 раз (всего до ~25 секунд для медленных ответов)
        let attempts = 0;
        checkIntervalRef.current = setInterval(async () => {
          if (responseReceived) {
            // Ответ уже получен, останавливаем проверку
            if (checkIntervalRef.current) {
              clearInterval(checkIntervalRef.current);
              checkIntervalRef.current = null;
            }
            setLoading(false);
            return;
          }
          
          attempts++;
          const received = await checkForResponse();
          
          // Останавливаем проверку если получили ответ или прошло 15 попыток
          if (received || attempts >= 15) {
            if (checkIntervalRef.current) {
              clearInterval(checkIntervalRef.current);
              checkIntervalRef.current = null;
            }
            setLoading(false);
            responseReceived = true;
          }
        }, 1500); // Проверяем каждые 1.5 секунды
      }, 2000); // Начинаем проверку через 2 секунды
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

  try {
    return (
      <div className="chat-interface">
        <div 
          className="chat-messages" 
          ref={messagesContainerRef}
        >
          {messages.length === 0 ? (
            <div className="empty-chat">
              <p>Начните диалог, отправив сообщение</p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id || `msg-${Date.now()}-${Math.random()}`}
                className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
              >
                <div className="message-content">{message.content || message.text || ''}</div>
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
        <div className="chat-bottom-side">
          <div className="chat-btn-actions">
            {
              actions.map((action) => (
                <div className="btn-action-box" onClick={action.effect} key={action.key}>
                  <div className="btn-action-content">{action.title}</div>
                </div>
              ))
            }
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
      </div>
    );
  } catch (error) {
    console.error('Error rendering ChatInterface:', error);
    return (
      <div className="chat-interface">
        <div className="chat-error">
          <h2>Ошибка</h2>
          <p>{error.message || 'Произошла ошибка при загрузке чата'}</p>
          {onChatNotFound && (
            <button onClick={onChatNotFound} className="back-button">
              Вернуться на главную
            </button>
          )}
        </div>
      </div>
    );
  }
}

export default ChatInterface;

