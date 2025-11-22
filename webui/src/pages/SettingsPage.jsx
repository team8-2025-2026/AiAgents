import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../api/auth';
import { authUtils } from '../utils/auth';
import '../styles/SettingsPage.css';

function SettingsPage() {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const user = authUtils.getUser();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (newPassword !== confirmPassword) {
      setError('Новый пароль и подтверждение не совпадают');
      return;
    }

    if (newPassword.length < 8 || newPassword.length > 32) {
      setError('Пароль должен быть от 8 до 32 символов');
      return;
    }

    setLoading(true);

    try {
      // Сначала проверяем старый пароль через логин
      const loginResponse = await authAPI.login(user.email, oldPassword);
      
      if (!loginResponse.success) {
        setError('Неверный текущий пароль');
        setLoading(false);
        return;
      }

      // Обновляем пароль
      const updateResponse = await authAPI.updateUser(
        user.email,
        user.access_token,
        { password: newPassword }
      );

      if (updateResponse.success) {
        setSuccess('Пароль успешно изменен');
        setOldPassword('');
        setNewPassword('');
        setConfirmPassword('');
        // Обновляем данные пользователя
        authUtils.updateUser(updateResponse.data);
      } else {
        setError(updateResponse.error || 'Ошибка при изменении пароля');
      }
    } catch (err) {
      setError('Ошибка подключения к серверу');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="settings-page">
      <div className="settings-container">
        <h1>Настройки</h1>
        <form onSubmit={handleSubmit} className="settings-form">
          <div className="form-group">
            <label htmlFor="oldPassword">Текущий пароль</label>
            <input
              id="oldPassword"
              type="password"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              required
              placeholder="Введите текущий пароль"
            />
          </div>
          <div className="form-group">
            <label htmlFor="newPassword">Новый пароль</label>
            <input
              id="newPassword"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              placeholder="Введите новый пароль"
              minLength={8}
              maxLength={32}
            />
          </div>
          <div className="form-group">
            <label htmlFor="confirmPassword">Подтверждение пароля</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              placeholder="Подтвердите новый пароль"
              minLength={8}
              maxLength={32}
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}
          <div className="form-actions">
            <button type="submit" disabled={loading} className="submit-button">
              {loading ? 'Сохранение...' : 'Изменить пароль'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/')}
              className="cancel-button"
            >
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SettingsPage;



