import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authUtils } from '../utils/auth';
import '../styles/UserPage.css';

function UserPage() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const userData = authUtils.getUser();
    if (!userData) {
      navigate('/auth');
      return;
    }
    setUser(userData);
  }, [navigate]);

  const getStatusLabel = (status) => {
    const labels = {
      STUDENT: 'Студент',
      TEACHER: 'Учитель',
      ASSISTENT: 'Поддержка',
    };
    return labels[status] || status;
  };

  if (!user) {
    return <div>Загрузка...</div>;
  }

  return (
    <div className="user-page">
      <div className="user-container">
        <h1>Профиль пользователя</h1>
        <div className="user-info">
          <div className="info-row">
            <span className="label">Email:</span>
            <span className="value">{user.email}</span>
          </div>
          <div className="info-row">
            <span className="label">Имя:</span>
            <span className="value">{user.first_name}</span>
          </div>
          <div className="info-row">
            <span className="label">Фамилия:</span>
            <span className="value">{user.last_name}</span>
          </div>
          <div className="info-row">
            <span className="label">Статус:</span>
            <span className="value">{getStatusLabel(user.status)}</span>
          </div>
          <div className="info-row">
            <span className="label">Описание:</span>
            <span className="value">{user.description || 'Не указано'}</span>
          </div>
        </div>
        <div className="user-actions">
          <button onClick={() => navigate('/settings')} className="action-button">
            Настройки
          </button>
          <button onClick={() => navigate('/')} className="action-button">
            На главную
          </button>
        </div>
      </div>
    </div>
  );
}

export default UserPage;



