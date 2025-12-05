/**
 * Скрипт страницы авторизации (index.html)
 * Обработка форм входа и регистрации
 */

document.addEventListener('DOMContentLoaded', () => {
    // Проверяем, авторизован ли пользователь
    if (api.isAuthenticated()) {
        window.location.href = '/rooms.html';
        return;
    }
    
    // Элементы DOM
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const alertContainer = document.getElementById('alertContainer');
    
    // Переключение табов
    loginTab.addEventListener('click', () => {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
        clearAlert();
    });
    
    registerTab.addEventListener('click', () => {
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        registerForm.classList.add('active');
        loginForm.classList.remove('active');
        clearAlert();
    });
    
    // Обработка формы входа
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        const submitBtn = loginForm.querySelector('button[type="submit"]');
        
        try {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Вход...';
            
            await api.login(email, password);
            
            showAlert('Вход выполнен успешно! Перенаправление...', 'success');
            
            setTimeout(() => {
                window.location.href = '/rooms.html';
            }, 500);
            
        } catch (error) {
            showAlert(error.message || 'Ошибка при входе', 'danger');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Войти';
        }
    });
    
    // Обработка формы регистрации
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('registerEmail').value;
        const displayName = document.getElementById('registerName').value;
        const password = document.getElementById('registerPassword').value;
        const confirmPassword = document.getElementById('registerConfirmPassword').value;
        const submitBtn = registerForm.querySelector('button[type="submit"]');
        
        // Проверка совпадения паролей
        if (password !== confirmPassword) {
            showAlert('Пароли не совпадают', 'danger');
            return;
        }
        
        // Проверка длины пароля
        if (password.length < 6) {
            showAlert('Пароль должен содержать минимум 6 символов', 'danger');
            return;
        }
        
        try {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Регистрация...';
            
            await api.register(email, displayName, password);
            
            showAlert('Регистрация успешна! Теперь войдите в систему.', 'success');
            
            // Переключаем на форму входа
            setTimeout(() => {
                loginTab.click();
                document.getElementById('loginEmail').value = email;
            }, 1500);
            
        } catch (error) {
            showAlert(error.message || 'Ошибка при регистрации', 'danger');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Зарегистрироваться';
        }
    });
    
    // Функция отображения алерта
    function showAlert(message, type = 'info') {
        alertContainer.innerHTML = `
            <div class="alert alert-${type}">
                ${message}
            </div>
        `;
    }
    
    // Функция очистки алерта
    function clearAlert() {
        alertContainer.innerHTML = '';
    }
});
