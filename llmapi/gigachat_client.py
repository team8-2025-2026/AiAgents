"""
Клиент для работы с GigaChat API от Сбера
Основан на официальной документации GigaChat API
"""

import os
import base64
import requests
import time
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class GigaChatConfig:
    """Конфигурация для GigaChat API"""
    client_id: str
    client_secret: str
    scope: str = "GIGACHAT_API_PERS"
    auth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    api_url: str = "https://gigachat.devices.sberbank.ru/api/v1"


class GigaChatClient:
    """Клиент для работы с GigaChat API"""
    
    def __init__(self, config: GigaChatConfig):
        self.config = config
        self.access_token: Optional[str] = None
        self.token_expires_at: float = 0
    
    def _get_access_token(self) -> str:
        """
        Получает access token для работы с API
        Использует OAuth 2.0 авторизацию
        """
        # Если токен еще действителен, возвращаем его
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        # Получаем новый токен
        auth_data = {
            "scope": self.config.scope
        }
        
        auth_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(int(time.time() * 1000)),  # Уникальный идентификатор запроса
            "Authorization": f"Basic {self._get_basic_auth()}"
        }
        
        try:
            response = requests.post(
                f"{self.config.auth_url}/token",
                data=auth_data,
                headers=auth_headers,
                verify=True  # В продакшене может потребоваться сертификат
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            # OAuth2 обычно возвращает expires_in (секунды до истечения)
            # или expires_at (время истечения). Проверяем оба варианта
            expires_in = token_data.get("expires_in")
            if expires_in is None:
                expires_at = token_data.get("expires_at")
                if expires_at:
                    expires_in = expires_at - time.time()
                else:
                    expires_in = 1800  # По умолчанию 30 минут
            
            # Устанавливаем время истечения с запасом в 5 минут
            self.token_expires_at = time.time() + expires_in - 300
            
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка получения токена доступа: {str(e)}")
    
    def _get_basic_auth(self) -> str:
        """
        Создает Basic Auth строку из client_id и client_secret
        """
        credentials = f"{self.config.client_id}:{self.config.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return encoded
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "GigaChat",
        temperature: float = 0.7,
        max_tokens: int = 512,
        stream: bool = False
    ) -> Dict:
        """
        Отправляет запрос на генерацию ответа в GigaChat
        
        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "текст"}]
            model: Модель для использования (по умолчанию "GigaChat")
            temperature: Температура генерации (0.0-1.0)
            max_tokens: Максимальное количество токенов в ответе
            stream: Использовать ли потоковую генерацию
        
        Returns:
            Словарь с ответом от API
        """
        access_token = self._get_access_token()
        
        url = f"{self.config.api_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                verify=True
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при запросе к GigaChat API: {str(e)}")
    
    def get_models(self) -> List[Dict]:
        """
        Получает список доступных моделей
        
        Returns:
            Список доступных моделей
        """
        access_token = self._get_access_token()
        
        url = f"{self.config.api_url}/models"
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        try:
            response = requests.get(
                url,
                headers=headers,
                verify=True
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при получении списка моделей: {str(e)}")


def create_gigachat_client_from_env() -> Optional[GigaChatClient]:
    """
    Создает клиент GigaChat из переменных окружения
    
    Ожидаемые переменные:
    - GIGACHAT_CLIENT_ID: Client ID для OAuth
    - GIGACHAT_CLIENT_SECRET: Client Secret для OAuth
    - GIGACHAT_SCOPE: Scope для доступа (опционально, по умолчанию GIGACHAT_API_PERS)
    
    Returns:
        GigaChatClient или None, если переменные не заданы
    """
    client_id = os.getenv("GIGACHAT_CLIENT_ID")
    client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
    scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
    
    if not client_id or not client_secret:
        return None
    
    config = GigaChatConfig(
        client_id=client_id,
        client_secret=client_secret,
        scope=scope
    )
    
    return GigaChatClient(config)

