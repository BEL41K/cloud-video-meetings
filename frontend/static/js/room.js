/**
 * Скрипт страницы комнаты видеоконференции (room.html)
 * Управление комнатой, чатом и списком участников
 */

document.addEventListener('DOMContentLoaded', () => {
    // Проверка авторизации
    if (!api.isAuthenticated()) {
        window.location.href = '/';
        return;
    }
    
    // Получаем ID комнаты из URL
    const urlParams = new URLSearchParams(window.location.search);
    const roomId = urlParams.get('id');
    
    if (!roomId) {
        window.location.href = '/rooms.html';
        return;
    }
    
    // Элементы DOM
    const userNameSpan = document.getElementById('userName');
    const logoutBtn = document.getElementById('logoutBtn');
    const roomNameEl = document.getElementById('roomName');
    const participantsList = document.getElementById('participantsList');
    const participantCount = document.getElementById('participantCount');
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendMessageBtn = document.getElementById('sendMessageBtn');
    const leaveRoomBtn = document.getElementById('leaveRoomBtn');
    
    let currentUser = null;
    let roomData = null;
    let updateInterval = null;
    let messagesInterval = null;
    
    // Инициализация страницы
    init();
    
    async function init() {
        try {
            // Загружаем данные пользователя
            currentUser = await api.getMe();
            userNameSpan.textContent = currentUser.display_name;
            
            // Присоединяемся к комнате
            await api.joinRoom(roomId);
            
            // Загружаем данные комнаты
            await loadRoom();
            
            // Загружаем сообщения
            await loadMessages();
            
            // Запускаем интервалы обновления
            updateInterval = setInterval(loadRoom, 5000); // Обновление участников каждые 5 секунд
            messagesInterval = setInterval(loadMessages, 1500); // Обновление чата каждые 1.5 секунды
            
        } catch (error) {
            console.error('Ошибка инициализации:', error);
            alert('Ошибка входа в комнату: ' + error.message);
            window.location.href = '/rooms.html';
        }
    }
    
    // Загрузка данных комнаты
    async function loadRoom() {
        try {
            roomData = await api.getRoom(roomId);
            
            roomNameEl.textContent = roomData.name;
            document.title = `${roomData.name} - CloudMeet Lite`;
            
            renderParticipants(roomData.participants);
            
        } catch (error) {
            console.error('Ошибка загрузки комнаты:', error);
        }
    }
    
    // Отрисовка списка участников
    function renderParticipants(participants) {
        participantCount.textContent = participants.length;
        
        if (participants.length === 0) {
            participantsList.innerHTML = '<p class="text-center" style="color: #6c757d; padding: 20px;">Нет участников</p>';
            return;
        }
        
        participantsList.innerHTML = participants.map(p => `
            <div class="participant-item">
                <div class="participant-avatar">
                    ${getInitials(p.user_display_name)}
                </div>
                <div class="participant-info">
                    <div class="participant-name">
                        ${p.is_owner ? '👑 ' : ''}${escapeHtml(p.user_display_name)}
                        ${p.user_id === currentUser?.id ? ' (Вы)' : ''}
                    </div>
                    <div class="participant-status ${p.status === 'in_call' ? 'in-call' : ''}">
                        ${p.status === 'in_call' ? '🟢 В конференции' : '⚪ Онлайн'}
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    // Загрузка сообщений
    async function loadMessages() {
        try {
            const response = await api.getMessages(roomId);
            renderMessages(response.messages);
        } catch (error) {
            console.error('Ошибка загрузки сообщений:', error);
        }
    }
    
    // Отрисовка сообщений
    function renderMessages(messages) {
        if (!messages || messages.length === 0) {
            chatMessages.innerHTML = '<p class="text-center" style="color: #6c757d; padding: 40px;">Сообщений пока нет. Начните общение!</p>';
            return;
        }
        
        const wasScrolledToBottom = chatMessages.scrollHeight - chatMessages.clientHeight <= chatMessages.scrollTop + 50;
        
        chatMessages.innerHTML = messages.map(msg => `
            <div class="chat-message ${msg.user_id === currentUser?.id ? 'own' : ''}">
                <div class="message-header">
                    <span class="message-author">${msg.is_owner ? '👑 ' : ''}${escapeHtml(msg.user_display_name)}</span>
                    <span class="message-time">${formatTime(msg.created_at)}</span>
                </div>
                <div class="message-content">${escapeHtml(msg.content)}</div>
            </div>
        `).join('');
        
        // Прокручиваем вниз если были внизу
        if (wasScrolledToBottom) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    // Отправка сообщения
    async function sendMessage() {
        const content = messageInput.value.trim();
        
        if (!content) {
            return;
        }
        
        try {
            sendMessageBtn.disabled = true;
            
            await api.sendMessage(roomId, content);
            
            messageInput.value = '';
            
            // Сразу обновляем сообщения
            await loadMessages();
            
            // Прокручиваем вниз
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
        } catch (error) {
            console.error('Ошибка отправки сообщения:', error);
            alert('Ошибка отправки сообщения: ' + error.message);
        } finally {
            sendMessageBtn.disabled = false;
            messageInput.focus();
        }
    }
    
    // Обработчики событий
    sendMessageBtn.addEventListener('click', sendMessage);
    
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Выход из комнаты
    leaveRoomBtn.addEventListener('click', async () => {
        try {
            // Останавливаем интервалы
            if (updateInterval) clearInterval(updateInterval);
            if (messagesInterval) clearInterval(messagesInterval);
            
            await api.leaveRoom(roomId);
            window.location.href = '/rooms.html';
            
        } catch (error) {
            console.error('Ошибка выхода из комнаты:', error);
            window.location.href = '/rooms.html';
        }
    });
    
    // Выход из системы
    logoutBtn.addEventListener('click', async () => {
        try {
            if (updateInterval) clearInterval(updateInterval);
            if (messagesInterval) clearInterval(messagesInterval);
            
            await api.leaveRoom(roomId);
        } catch (error) {
            console.error('Ошибка при выходе:', error);
        }
        
        api.logout();
    });
    
    // Обработка закрытия страницы
    window.addEventListener('beforeunload', () => {
        if (updateInterval) clearInterval(updateInterval);
        if (messagesInterval) clearInterval(messagesInterval);
        
        // Пытаемся выйти из комнаты
        navigator.sendBeacon(`${api.baseUrl}/rooms/${roomId}/leave`, JSON.stringify({}));
    });
    
    // Вспомогательные функции
    function getInitials(name) {
        if (!name) return '?';
        const parts = name.trim().split(' ');
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return name.substring(0, 2).toUpperCase();
    }
    
    function formatTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
