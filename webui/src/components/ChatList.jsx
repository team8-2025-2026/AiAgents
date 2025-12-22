import React, { useState, useMemo } from 'react';
import '../styles/ChatList.css';

function ChatList({
  chats,
  selectedChatId,
  onChatSelect,
  onNewChat,
  onChatDelete,
  onChatRename,
  userStatus,
  filters,
  onFiltersChange,
}) {
  const [editingChatId, setEditingChatId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const handleStartEdit = (chat) => {
    setEditingChatId(chat.id);
    setEditTitle(chat.title);
  };

  const handleSaveEdit = (chatId) => {
    if (editTitle.trim()) {
      onChatRename(chatId, editTitle.trim());
    }
    setEditingChatId(null);
    setEditTitle('');
  };

  const handleCancelEdit = () => {
    setEditingChatId(null);
    setEditTitle('');
  };

  // Оптимизированная фильтрация чатов с useMemo
  const filteredChats = useMemo(() => {
    if (userStatus === 'TEACHER' && filters) {
      return chats.filter(chat => {
        if (filters.studentId && chat.student_id !== filters.studentId) return false;
        if (filters.status && chat.status !== filters.status) return false;
        return true;
      });
    }
    return chats;
  }, [chats, userStatus, filters]);

  return (
    <div className="chat-list">
      <div className="chat-list-header">
        {onNewChat && (
          <button onClick={onNewChat} className="new-chat-button">
            + Новый чат
          </button>
        )}
        {userStatus === 'TEACHER' && onFiltersChange && (
          <div className="chat-filters">
            <select
              value={filters?.status || 'all'}
              onChange={(e) => onFiltersChange({ ...filters, status: e.target.value === 'all' ? null : e.target.value })}
              className="filter-select"
            >
              <option value="all">Все статусы</option>
              <option value="open">Открытые</option>
              <option value="deleted">Удаленные</option>
            </select>
            <input
              type="text"
              placeholder="Фильтр по студенту"
              value={filters?.studentId || ''}
              onChange={(e) => onFiltersChange({ ...filters, studentId: e.target.value || null })}
              className="filter-input"
            />
          </div>
        )}
      </div>
      <div className="chat-list-content">
        {filteredChats.map((chat) => (
          <div
            key={chat.id}
            className={`chat-item ${selectedChatId === chat.id ? 'active' : ''}`}
            onClick={() => onChatSelect(chat.id)}
          >
            {editingChatId === chat.id ? (
              <div className="chat-edit">
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  onBlur={() => handleSaveEdit(chat.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSaveEdit(chat.id);
                    if (e.key === 'Escape') handleCancelEdit();
                  }}
                  autoFocus
                  className="chat-edit-input"
                />
              </div>
            ) : (
              <>
                <div className="chat-title">
                  {chat.title}
                  {chat.status === 'deleted' && <span className="deleted-badge">Удален</span>}
                </div>
                <div className="chat-actions">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleStartEdit(chat);
                    }}
                    className="chat-action-button"
                    title="Переименовать"
                  >
                    ✏️
                  </button>
                  {onChatDelete && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onChatDelete(chat.id);
                      }}
                      className="chat-action-button"
                      title="Удалить"
                    >
                      🗑️
                    </button>
                  )}
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default ChatList;

