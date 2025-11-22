import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../api/auth';
import { authUtils } from '../utils/auth';
import '../styles/ManagePage.css';

function ManagePage() {
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [status, setStatus] = useState('STUDENT');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedPassword, setGeneratedPassword] = useState('');
  const navigate = useNavigate();

  const user = authUtils.getUser();

  useEffect(() => {
    if (!user || user.status !== 'ASSISTENT') {
      navigate('/');
    }
  }, [user, navigate]);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setGeneratedPassword('');

    setLoading(true);

    try {
      const response = await authAPI.createUser(
        email,
        firstName,
        lastName,
        status,
        user.access_token
      );

      if (response.success) {
        setSuccess('Пользователь успешно создан');
        setGeneratedPassword(response.data.password);
        setEmail('');
        setFirstName('');
        setLastName('');
        setStatus('STUDENT');
      } else {
        setError(response.error || 'Ошибка при создании пользователя');
      }
    } catch (err) {
      setError('Ошибка подключения к серверу');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userEmail) => {
    if (!window.confirm(`Вы уверены, что хотите удалить пользователя ${userEmail}?`)) {
      return;
    }

    setError('');
    setSuccess('');

    try {
      const response = await authAPI.deleteUser(userEmail, user.access_token);

      if (response.success) {
        setSuccess(`Пользователь ${userEmail} успешно удален`);
      } else {
        setError(response.error || 'Ошибка при удалении пользователя');
      }
    } catch (err) {
      setError('Ошибка подключения к серверу');
      console.error(err);
    }
  };

  const getStatusLabel = (status) => {
    const labels = {
      STUDENT: 'Студент',
      TEACHER: 'Учитель',
      ASSISTENT: 'Поддержка',
    };
    return labels[status] || status;
  };

  if (!user || user.status !== 'ASSISTENT') {
    return null;
  }

  return (
    <div className="manage-page">
      <div className="manage-container">
        <h1>Управление пользователями</h1>
        
        <div className="create-user-section">
          <h2>Создать пользователя</h2>
          <form onSubmit={handleCreateUser} className="create-user-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="example@mail.com"
                />
              </div>
              <div className="form-group">
                <label htmlFor="status">Статус</label>
                <select
                  id="status"
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  required
                >
                  <option value="STUDENT">Студент</option>
                  <option value="TEACHER">Учитель</option>
                  <option value="ASSISTENT">Поддержка</option>
                </select>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="firstName">Имя</label>
                <input
                  id="firstName"
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  required
                  minLength={2}
                  maxLength={64}
                  placeholder="Имя"
                />
              </div>
              <div className="form-group">
                <label htmlFor="lastName">Фамилия</label>
                <input
                  id="lastName"
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  required
                  minLength={2}
                  maxLength={64}
                  placeholder="Фамилия"
                />
              </div>
            </div>
            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}
            {generatedPassword && (
              <div className="password-display">
                <strong>Сгенерированный пароль:</strong>
                <code>{generatedPassword}</code>
                <small>Сохраните этот пароль и отправьте пользователю</small>
              </div>
            )}
            <button type="submit" disabled={loading} className="submit-button">
              {loading ? 'Создание...' : 'Создать пользователя'}
            </button>
          </form>
        </div>

        <div className="actions">
          <button onClick={() => navigate('/')} className="back-button">
            На главную
          </button>
        </div>
      </div>
    </div>
  );
}

export default ManagePage;



