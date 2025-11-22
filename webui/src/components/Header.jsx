import React from 'react';
import { useNavigate } from 'react-router-dom';
import { authUtils } from '../utils/auth';
import '../styles/Header.css';

function Header({ user }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    authUtils.logout();
    navigate('/auth');
  };

  return (
    <div className="header">
      <div className="header-content">
        <div className="header-left">
          <h2>AI Agents</h2>
        </div>
        <div className="header-right">
          <button onClick={() => navigate('/user')} className="header-button">
            Профиль
          </button>
          <button onClick={handleLogout} className="header-button">
            Смена аккаунта
          </button>
        </div>
      </div>
    </div>
  );
}

export default Header;



