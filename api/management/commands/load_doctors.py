from django.core.management.base import BaseCommand
from api.models import Doctor, Service
from api.fixtures.doctors_data import DOCTORS_DATA


class Command(BaseCommand):
    help = 'Загрузка начальных данных врачей стоматологии'

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for doctor_data in DOCTORS_DATA:
            # Создаем или обновляем врача
            doctor, created = Doctor.objects.update_or_create(
                name=doctor_data['name'],
                defaults={
                    'specialty': doctor_data['specialty'],
                    'experience': doctor_data['experience'],
                    'education': doctor_data['education'],
                    'description': doctor_data['description'],
                    'is_active': True,
                    'working_hours': {
                        'пн': '09:00-18:00',
                        'вт': '09:00-18:00',
                        'ср': '09:00-18:00',
                        'чт': '09:00-18:00',
                        'пт': '09:00-18:00',
                        'сб': '10:00-16:00',
                        'вс': 'выходной'
                    }
                }
            )

            # Добавляем услуги врачу
            services_to_add = []
            for service_name in doctor_data['services_names']:
                try:
                    service = Service.objects.get(name=service_name)
                    services_to_add.append(service)
                except Service.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Услуга "{service_name}" не найдена для врача {doctor.name}')
                    )

            doctor.services.set(services_to_add)

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Создан врач: {doctor.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Обновлен врач: {doctor.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Загрузка завершена! Создано: {created_count}, Обновлено: {updated_count}'
            )
        )