from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Service, Doctor, Appointment
from django.contrib import messages
import json
from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    def each_context(self, request):
        context = super().each_context(request)
        context['site_header'] = 'Стоматология "Улыбка"'
        context['site_title'] = 'Панель управления'
        return context

# Замените стандартную админку на кастомную
admin_site = CustomAdminSite(name='custom_admin')
# Фильтры для админки
class StatusFilter(admin.SimpleListFilter):
    title = 'Статус записи'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('today', 'На сегодня'),
            ('future', 'Предстоящие'),
            ('past', 'Прошедшие'),
            ('pending', 'Ожидают подтверждения'),
        ]

    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == 'today':
            return queryset.filter(date=today)
        elif self.value() == 'future':
            return queryset.filter(date__gt=today)
        elif self.value() == 'past':
            return queryset.filter(date__lt=today)
        elif self.value() == 'pending':
            return queryset.filter(status='pending')
        return queryset


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration', 'is_active', 'get_appointments_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['price', 'duration', 'is_active']

    def get_appointments_count(self, obj):
        return obj.appointment_set.count()

    get_appointments_count.short_description = 'Кол-во записей'


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty', 'experience', 'is_active', 'get_photo', 'get_appointments_count']
    list_filter = ['specialty', 'is_active']
    search_fields = ['name', 'specialty', 'education']
    filter_horizontal = ['services']
    readonly_fields = ['get_photo_preview']

    def get_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />',
                               obj.photo.url)
        return "—"

    get_photo.short_description = 'Фото'

    def get_photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="200" style="border-radius: 8px;" />', obj.photo.url)
        return "Фото не загружено"

    get_photo_preview.short_description = 'Предпросмотр фото'

    def get_appointments_count(self, obj):
        count = obj.appointment_set.count()
        url = reverse('admin:api_appointment_changelist') + f'?doctor__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, count)

    get_appointments_count.short_description = 'Записей'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'patient_name',
        'patient_phone',
        'doctor',
        'service',
        'date',
        'time',
        'get_status_display',
        'created_at'
    ]
    list_filter = [StatusFilter, 'status', 'date', 'doctor', 'service']
    search_fields = ['patient_name', 'patient_phone', 'patient_email', 'doctor__name']
    readonly_fields = ['created_at', 'updated_at', 'get_timeline']
    date_hierarchy = 'date'
    actions = ['confirm_selected', 'cancel_selected', 'mark_completed']

    fieldsets = (
        ('Данные пациента', {
            'fields': ('patient_name', 'patient_phone', 'patient_email')
        }),
        ('Информация о записи', {
            'fields': ('service', 'doctor', 'date', 'time', 'status')
        }),
        ('Комментарии', {
            'fields': ('comment', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at', 'get_timeline'),
            'classes': ('collapse',)
        }),
    )

    def get_status_display(self, obj):
        status_colors = {
            'pending': 'warning',
            'confirmed': 'success',
            'cancelled': 'danger',
            'completed': 'info'
        }
        color = status_colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_status_display()
        )

    get_status_display.short_description = 'Статус'
    get_status_display.admin_order_field = 'status'

    def get_timeline(self, obj):
        timeline = f"""
        <div style="font-size: 12px;">
            <div>Создана: {obj.created_at.strftime('%d.%m.%Y %H:%M')}</div>
            <div>Обновлена: {obj.updated_at.strftime('%d.%m.%Y %H:%M')}</div>
        </div>
        """
        return format_html(timeline)

    get_timeline.short_description = 'Таймлайн'

    # Действия массового редактирования
    def confirm_selected(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} записей подтверждено.', messages.SUCCESS)

    confirm_selected.short_description = 'Подтвердить выбранные записи'

    def cancel_selected(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} записей отменено.', messages.WARNING)

    cancel_selected.short_description = 'Отменить выбранные записи'

    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} записей отмечено как завершенные.', messages.INFO)

    mark_completed.short_description = 'Отметить как завершенные'

    # Валидация при сохранении
    def save_model(self, request, obj, form, change):
        # Проверяем, не занято ли время у врача
        if change and 'date' in form.changed_data or 'time' in form.changed_data:
            conflicting = Appointment.objects.filter(
                doctor=obj.doctor,
                date=obj.date,
                time=obj.time
            ).exclude(pk=obj.pk)

            if conflicting.exists():
                self.message_user(
                    request,
                    'Внимание: Это время уже занято у выбранного врача!',
                    messages.WARNING
                )

        super().save_model(request, obj, form, change)


# Настройка админ-панели
admin.site.site_header = 'Панель управления стоматологической клиникой'
admin.site.site_title = 'Стоматология "Улыбка"'
admin.site.index_title = 'Статистика и управление'