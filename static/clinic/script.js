const API_BASE = '/api/';

// Функция для показа сообщений
function showMessage(text, type) {
    const msg = document.getElementById('message');
    msg.textContent = text;
    msg.className = `alert alert-${type} alert-dismissible fade show`;
    msg.style.display = 'block';

    // Добавляем кнопку закрытия
    msg.innerHTML = `
        ${text}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
        if (msg.style.display !== 'none') {
            msg.style.display = 'none';
        }
    }, 5000);
}

// Загрузка услуг для главной страницы
async function loadServices() {
    try {
        console.log('Загрузка услуг...');
        const response = await fetch(API_BASE + 'services/');
        console.log('Ответ сервера (услуги):', response.status);

        if (!response.ok) {
            throw new Error(`Ошибка HTTP: ${response.status}`);
        }

        const services = await response.json();
        console.log('Получено услуг:', services.length);

        const container = document.getElementById('servicesContainer');

        if (services.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center">
                    <div class="alert alert-info">
                        Услуги временно недоступны
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = ''; // Очищаем спиннер

        services.forEach(service => {
            const col = document.createElement('div');
            col.className = 'col-md-4 mb-4';
            col.innerHTML = `
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">${service.name}</h5>
                        <p class="card-text">${service.description || 'Описание услуги'}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="text-primary fw-bold">${service.price} руб.</span>
                            <small class="text-muted">${service.duration || 30} мин.</small>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(col);
        });

    } catch (error) {
        console.error('Ошибка загрузки услуг:', error);
        const container = document.getElementById('servicesContainer');
        container.innerHTML = `
            <div class="col-12 text-center">
                <div class="alert alert-warning">
                    Не удалось загрузить услуги. Пожалуйста, обновите страницу.
                </div>
            </div>
        `;
    }
}

// Загрузка врачей для главной страницы
async function loadDoctors() {
    try {
        console.log('Загрузка врачей...');
        const response = await fetch(API_BASE + 'doctors/');
        console.log('Ответ сервера (врачи):', response.status);

        if (!response.ok) {
            throw new Error(`Ошибка HTTP: ${response.status}`);
        }

        const doctors = await response.json();
        console.log('Получено врачей:', doctors.length);

        const container = document.getElementById('doctorsContainer');

        if (doctors.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center">
                    <div class="alert alert-info">
                        Врачи временно недоступны
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = ''; // Очищаем спиннер

        doctors.forEach(doctor => {
            const col = document.createElement('div');
            col.className = 'col-md-6 col-lg-4 mb-4';
            col.innerHTML = `
                <div class="card h-100">
                    <div class="card-body text-center">
                        <div class="doctor-photo mb-3">
                            <i class="fas fa-user-md fa-3x text-primary"></i>
                        </div>
                        <h5 class="card-title">${doctor.name}</h5>
                        <h6 class="card-subtitle mb-2 text-muted">${doctor.specialty}</h6>
                        <p class="card-text">
                            <small>Опыт работы: ${doctor.experience || 0} лет</small>
                        </p>
                        <p class="card-text small">${doctor.description || 'Опытный специалист'}</p>
                    </div>
                </div>
            `;
            container.appendChild(col);
        });

    } catch (error) {
        console.error('Ошибка загрузки врачей:', error);
        const container = document.getElementById('doctorsContainer');
        container.innerHTML = `
            <div class="col-12 text-center">
                <div class="alert alert-warning">
                    Не удалось загрузить врачей. Пожалуйста, обновите страницу.
                </div>
            </div>
        `;
    }
}

// Загрузка услуг для формы записи
async function loadServicesForForm() {
    try {
        const response = await fetch(API_BASE + 'services/');
        const services = await response.json();
        const select = document.getElementById('serviceSelect');

        select.innerHTML = '<option value="">-- Выберите услугу --</option>';
        services.forEach(service => {
            const option = document.createElement('option');
            option.value = service.id;
            option.textContent = `${service.name} (${service.price} руб.)`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Ошибка загрузки услуг для формы:', error);
        showMessage('Ошибка загрузки списка услуг', 'danger');
    }
}

// Загрузка врачей для формы записи
async function loadDoctorsForForm() {
    try {
        const response = await fetch(API_BASE + 'doctors/');
        const doctors = await response.json();
        const select = document.getElementById('doctorSelect');

        select.innerHTML = '<option value="">-- Выберите врача --</option>';
        doctors.forEach(doctor => {
            const option = document.createElement('option');
            option.value = doctor.id;
            option.textContent = `${doctor.name} - ${doctor.specialty}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Ошибка загрузки врачей для формы:', error);
        showMessage('Ошибка загрузки списка врачей', 'danger');
    }
}

// Обработчик формы записи
document.getElementById('appointmentForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        patient_name: document.getElementById('patientName').value.trim(),
        patient_phone: document.getElementById('patientPhone').value.trim(),
        patient_email: document.getElementById('patientEmail').value.trim(),
        service: parseInt(document.getElementById('serviceSelect').value),
        doctor: parseInt(document.getElementById('doctorSelect').value),
        date: document.getElementById('dateInput').value,
        time: document.getElementById('timeInput').value,
        comment: document.getElementById('commentInput').value.trim()
    };

    // Валидация
    if (!formData.patient_name) {
        return showMessage('Пожалуйста, введите ваше имя.', 'warning');
    }
    if (!formData.patient_phone) {
        return showMessage('Пожалуйста, введите ваш телефон.', 'warning');
    }
    if (!formData.service) {
        return showMessage('Пожалуйста, выберите услугу.', 'warning');
    }
    if (!formData.doctor) {
        return showMessage('Пожалуйста, выберите врача.', 'warning');
    }
    if (!formData.date || !formData.time) {
        return showMessage('Пожалуйста, выберите дату и время.', 'warning');
    }

    try {
        showMessage('Отправляем вашу заявку...', 'info');

        const response = await fetch(API_BASE + 'appointments/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (response.ok) {
            showMessage('✅ ' + result.message, 'success');
            document.getElementById('appointmentForm').reset();
            // Закрываем модальное окно через 2 секунды
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('appointmentModal'));
                if (modal) {
                    modal.hide();
                }
            }, 2000);
        } else {
            showMessage('❌ ' + (result.error || result.detail || 'Ошибка при отправке'), 'danger');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showMessage('❌ Ошибка соединения с сервером', 'danger');
    }
});

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Страница загружена, начинаем загрузку данных...');

    // Загружаем данные для главной страницы
    loadServices();
    loadDoctors();

    // Загружаем данные для формы
    loadServicesForForm();
    loadDoctorsForForm();

    // Устанавливаем минимальную дату (завтра)
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    document.getElementById('dateInput').min = tomorrow.toISOString().split('T')[0];

    // Плавная прокрутка для навигации
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});