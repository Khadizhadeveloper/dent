from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название услуги')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    duration = models.PositiveIntegerField(
        default=30,
        verbose_name='Длительность (мин)',
        help_text='Продолжительность приема в минутах'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    image = models.ImageField(
        upload_to='services/',
        blank=True,
        null=True,
        verbose_name='Изображение услуги'
    )

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.price} руб."


class Doctor(models.Model):
    name = models.CharField(max_length=100, verbose_name='ФИО врача')
    specialty = models.CharField(max_length=100, verbose_name='Специализация')
    services = models.ManyToManyField(Service, verbose_name='Услуги')
    experience = models.PositiveIntegerField(
        default=0,
        verbose_name='Стаж (лет)',
        help_text='Опыт работы в годах'
    )
    education = models.TextField(blank=True, verbose_name='Образование')
    description = models.TextField(blank=True, verbose_name='О враче')
    photo = models.ImageField(
        upload_to='doctors/',
        blank=True,
        null=True,
        verbose_name='Фотография'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    working_hours = models.JSONField(
        default=dict,
        verbose_name='График работы',
        help_text='JSON с графиком работы по дням недели'
    )

    class Meta:
        verbose_name = 'Врач'
        verbose_name_plural = 'Врачи'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.specialty}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', '⏳ Ожидает подтверждения'),
        ('confirmed', '✅ Подтверждена'),
        ('cancelled', '❌ Отменена'),
        ('completed', '✅ Завершена'),
    ]

    # Данные пациента (с временным default)
    patient_name = models.CharField(
        max_length=100,
        verbose_name='ФИО пациента',
        default="Неизвестный пациент"  # Добавляем временный default
    )
    patient_phone = models.CharField(
        max_length=20,
        verbose_name='Телефон пациента',
        default="+70000000000"  # Добавляем временный default
    )
    patient_email = models.EmailField(
        blank=True,
        verbose_name='Email пациента'
    )

    # Остальные поля без изменений...
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Услуга')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name='Врач')
    date = models.DateField(verbose_name='Дата приема')
    time = models.TimeField(verbose_name='Время приема')
    comment = models.TextField(blank=True, verbose_name='Комментарий пациента')
    admin_notes = models.TextField(blank=True, verbose_name='Заметки администратора')

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Запись на прием'
        verbose_name_plural = 'Записи на прием'
        ordering = ['-date', '-time']
        unique_together = ['doctor', 'date', 'time']

    def __str__(self):
        return f"{self.patient_name} - {self.doctor.name} - {self.date} {self.time}"

    def get_duration(self):
        return self.service.duration if self.service else 30

    def get_end_time(self):
        from datetime import datetime, timedelta
        if self.time:
            start_time = datetime.combine(self.date, self.time)
            end_time = start_time + timedelta(minutes=self.get_duration())
            return end_time.time()
        return None