from rest_framework import generics, status, serializers  # Добавил импорт serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Service, Doctor, Appointment
from .serializers import (
    ServiceSerializer, DoctorSerializer,
    AppointmentCreateSerializer
)
from django.shortcuts import render

from datetime import date as datetime_date



def home(request):
    services = Service.objects.filter(is_active=True)
    doctors = Doctor.objects.filter(is_active=True)
    return render(request, 'clinic/index.html', {'services': services, 'doctors': doctors})

# Публичные: услуги и доктора
class ServiceList(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Service.objects.filter(is_active=True)  # Добавил фильтр по активным
    serializer_class = ServiceSerializer


class DoctorList(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Doctor.objects.filter(is_active=True)  # Добавил фильтр по активным
    serializer_class = DoctorSerializer


# Создание записи (БЕЗ авторизации)
class AppointmentCreate(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = Appointment.objects.all()
    serializer_class = AppointmentCreateSerializer

    def perform_create(self, serializer):
        # Валидация: проверить пересечение времени у доктора
        doctor = serializer.validated_data['doctor']
        date = serializer.validated_data['date']
        time = serializer.validated_data['time']

        # Проверяем, не занято ли время у этого врача
        if Appointment.objects.filter(
            doctor=doctor,
            date=date,
            time=time,
            status__in=['confirmed', 'pending']  # Проверяем только активные записи
        ).exists():
            raise serializers.ValidationError("Это время уже занято у доктора. Пожалуйста, выберите другое время.")

        # Проверяем, что дата не в прошлом
        if date < datetime_date.today():
            raise serializers.ValidationError("Нельзя записаться на прошедшую дату.")

        # Сохраняем запись со статусом "ожидает подтверждения"
        serializer.save(status='pending')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                # Успешный ответ
                return Response({
                    "message": "Запись успешно отправлена! Наш администратор свяжется с вами для подтверждения."
                }, status=status.HTTP_201_CREATED)

            except serializers.ValidationError as e:
                # Ловим конкретную ошибку валидации из perform_create
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)