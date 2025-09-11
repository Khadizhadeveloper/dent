from django.core.management.base import BaseCommand
from api.models import Service
from api.fixtures.services_data import SERVICES_DATA


class Command(BaseCommand):
    help = 'Загрузка начальных данных услуг стоматологии'

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for service_data in SERVICES_DATA:
            service, created = Service.objects.update_or_create(
                name=service_data['name'],
                defaults={
                    'description': service_data['description'],
                    'price': service_data['price'],
                    'duration': service_data['duration'],
                    'is_active': True
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Создана услуга: {service.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Обновлена услуга: {service.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Загрузка завершена! Создано: {created_count}, Обновлено: {updated_count}'
            )
        )