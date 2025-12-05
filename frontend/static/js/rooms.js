/**
 * Скрипт страницы списка комнат (rooms.html)
 * Отображение и управление комнатами
 */

document.addEventListener('DOMContentLoaded', () => {
    // Проверка авторизации
    if (!api.isAuthenticated()) {
        window.location.href = '/';
        return;
    }
    
    // Элементы DOM
    const userNameSpan = document.getElementById('userName');
    const logoutBtn = document.getElementById('logoutBtn');
    const roomsList = document.getElementById('roomsList');
    const createRoomBtn = document.getElementById('createRoomBtn');
    const createRoomModal = document.getElementById('createRoomModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const createRoomForm = document.getElementById('createRoomForm');
    const alertContainer = document.getElementById('alertContainer');
    
    let currentUser = null;
    
    // Инициализация страницы
    init();
    
    async function init() {
        try {
            // Загружаем данные пользователя
            currentUser = await api.getMe();
            userNameSpan.textContent = currentUser.display_name;
            
            // Загружаем список комнат
            await loadRooms();
            
        } catch (error) {
            showAlert('Ошибка загрузки данных: ' + error.message, 'danger');
        }
    }
    
    // Загрузка списка комнат
    async function loadRooms() {
        try {
            const rooms = await api.getRooms();
            renderRooms(rooms);
        } catch (error) {
            showAlert('Ошибка загрузки комнат: ' + error.message, 'danger');
        }
    }
    
    // Отрисовка списка комнат
    function renderRooms(rooms) {
        if (!rooms || rooms.length === 0) {
            roomsList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📹</div>
                    <h3>Нет доступных комнат</h3>
                    <p>Создайте первую комнату для видеоконференции</p>
                    <button class="btn btn-primary" onclick="document.getElementById('createRoomBtn').click()">
                        Создать комнату
                    </button>
                </div>
            `;
            return;
        }
        
        roomsList.innerHTML = rooms.map(room => `
            <div class="room-card" data-room-id="${room.id}">
                <div class="room-info">
                    <div class="room-name">${escapeHtml(room.name)}</div>
                    <div class="room-meta">
                        <span>
                            <span class="participants-count ${room.participants_count > 0 ? 'active' : ''}">
                                👥 ${room.participants_count} участник(ов)
                            </span>
                        </span>
                        <span>📅 ${formatDate(room.created_at)}</span>
                    </div>
                </div>
                <div class="room-actions">
                    <button class="btn btn-primary btn-sm join-room-btn" data-room-id="${room.id}">
                        Войти
                    </button>
                    ${room.owner_id === currentUser?.id ? `
                        <button class="btn btn-danger btn-sm delete-room-btn" data-room-id="${room.id}">
                            Удалить
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
        
        // Добавляем обработчики для кнопок
        document.querySelectorAll('.join-room-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const roomId = e.target.dataset.roomId;
                joinRoom(roomId);
            });
        });
        
        document.querySelectorAll('.delete-room-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const roomId = e.target.dataset.roomId;
                deleteRoom(roomId);
            });
        });
    }
    
    // Присоединение к комнате
    async function joinRoom(roomId) {
        try {
            await api.joinRoom(roomId);
            window.location.href = `/room.html?id=${roomId}`;
        } catch (error) {
            showAlert('Ошибка при присоединении: ' + error.message, 'danger');
        }
    }
    
    // Удаление комнаты
    async function deleteRoom(roomId) {
        if (!confirm('Вы уверены, что хотите удалить эту комнату?')) {
            return;
        }
        
        try {
            await api.deleteRoom(roomId);
            showAlert('Комната удалена', 'success');
            await loadRooms();
        } catch (error) {
            showAlert('Ошибка при удалении: ' + error.message, 'danger');
        }
    }
    
    // Открытие модального окна
    createRoomBtn.addEventListener('click', () => {
        createRoomModal.classList.remove('hidden');
        document.getElementById('roomName').focus();
    });
    
    // Закрытие модального окна
    closeModalBtn.addEventListener('click', () => {
        createRoomModal.classList.add('hidden');
    });
    
    createRoomModal.addEventListener('click', (e) => {
        if (e.target === createRoomModal) {
            createRoomModal.classList.add('hidden');
        }
    });
    
    // Создание комнаты
    createRoomForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const roomName = document.getElementById('roomName').value.trim();
        const submitBtn = createRoomForm.querySelector('button[type="submit"]');
        
        if (!roomName) {
            showAlert('Введите название комнаты', 'danger');
            return;
        }
        
        try {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Создание...';
            
            const room = await api.createRoom(roomName);
            
            createRoomModal.classList.add('hidden');
            document.getElementById('roomName').value = '';
            
            showAlert('Комната создана!', 'success');
            
            // Сразу входим в комнату
            setTimeout(() => {
                window.location.href = `/room.html?id=${room.id}`;
            }, 500);
            
        } catch (error) {
            showAlert('Ошибка создания комнаты: ' + error.message, 'danger');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Создать';
        }
    });
    
    // Выход из системы
    logoutBtn.addEventListener('click', () => {
        api.logout();
    });
    
    // Вспомогательные функции
    function showAlert(message, type = 'info') {
        alertContainer.innerHTML = `
            <div class="alert alert-${type}">
                ${message}
            </div>
        `;
        
        setTimeout(() => {
            alertContainer.innerHTML = '';
        }, 5000);
    }
    
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
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
