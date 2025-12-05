/**
 * API клиент для CloudMeet Lite
 * Обертка над fetch для работы с backend API
 */

// Базовый URL API (настраивается через переменные окружения или конфигурацию)
const API_BASE_URL = window.API_BASE_URL || '/api';

/**
 * Класс для работы с API
 */
class ApiClient {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }
    
    /**
     * Получение токена из localStorage
     */
    getToken() {
        return localStorage.getItem('token');
    }
    
    /**
     * Сохранение токена в localStorage
     */
    setToken(token) {
        localStorage.setItem('token', token);
    }
    
    /**
     * Удаление токена из localStorage
     */
    removeToken() {
        localStorage.removeItem('token');
    }
    
    /**
     * Проверка авторизации
     */
    isAuthenticated() {
        return !!this.getToken();
    }
    
    /**
     * Формирование заголовков запроса
     */
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (includeAuth && this.getToken()) {
            headers['Authorization'] = `Bearer ${this.getToken()}`;
        }
        
        return headers;
    }
    
    /**
     * Выполнение HTTP запроса
     */
    async request(method, endpoint, data = null, includeAuth = true) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const options = {
            method,
            headers: this.getHeaders(includeAuth)
        };
        
        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(url, options);
            
            // Для 204 No Content
            if (response.status === 204) {
                return { success: true };
            }
            
            const responseData = await response.json();
            
            if (!response.ok) {
                // Если токен недействителен, выходим
                if (response.status === 401) {
                    this.removeToken();
                    window.location.href = '/';
                    return;
                }
                
                throw new Error(responseData.detail || 'Произошла ошибка');
            }
            
            return responseData;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    
    // === Методы аутентификации ===
    
    /**
     * Регистрация нового пользователя
     */
    async register(email, displayName, password) {
        return this.request('POST', '/auth/register', {
            email,
            display_name: displayName,
            password
        }, false);
    }
    
    /**
     * Вход в систему
     */
    async login(email, password) {
        const response = await this.request('POST', '/auth/login', {
            email,
            password
        }, false);
        
        if (response.access_token) {
            this.setToken(response.access_token);
        }
        
        return response;
    }
    
    /**
     * Получение данных текущего пользователя
     */
    async getMe() {
        return this.request('GET', '/auth/me');
    }
    
    /**
     * Выход из системы
     */
    logout() {
        this.removeToken();
        window.location.href = '/';
    }
    
    // === Методы для работы с комнатами ===
    
    /**
     * Получение списка комнат
     */
    async getRooms(skip = 0, limit = 20, onlyActive = true) {
        return this.request('GET', `/rooms?skip=${skip}&limit=${limit}&only_active=${onlyActive}`);
    }
    
    /**
     * Получение информации о комнате
     */
    async getRoom(roomId) {
        return this.request('GET', `/rooms/${roomId}`);
    }
    
    /**
     * Создание новой комнаты
     */
    async createRoom(name) {
        return this.request('POST', '/rooms', { name });
    }
    
    /**
     * Присоединение к комнате
     */
    async joinRoom(roomId) {
        return this.request('POST', `/rooms/${roomId}/join`);
    }
    
    /**
     * Выход из комнаты
     */
    async leaveRoom(roomId) {
        return this.request('POST', `/rooms/${roomId}/leave`);
    }
    
    /**
     * Удаление комнаты
     */
    async deleteRoom(roomId) {
        return this.request('DELETE', `/rooms/${roomId}`);
    }
    
    // === Методы для работы с сообщениями ===
    
    /**
     * Получение сообщений комнаты
     */
    async getMessages(roomId, skip = 0, limit = 50) {
        return this.request('GET', `/rooms/${roomId}/messages?skip=${skip}&limit=${limit}`);
    }
    
    /**
     * Отправка сообщения в комнату
     */
    async sendMessage(roomId, content) {
        return this.request('POST', `/rooms/${roomId}/messages`, { content });
    }
}

// Глобальный экземпляр API клиента
const api = new ApiClient();
