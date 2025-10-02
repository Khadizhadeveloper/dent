from rest_framework import serializers
from .models import Service, Doctor, Appointment



class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class DoctorSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Doctor
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

class AppointmentCreateSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(max_length=100, write_only=True)
    patient_phone = serializers.CharField(max_length=20, write_only=True)
    patient_email = serializers.EmailField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Appointment
        fields = [
            'patient_name', 'patient_phone', 'patient_email',
            'service', 'doctor', 'date', 'time', 'comment'
        ]

    def validate(self, attrs):

        patient_name = attrs.get('patient_name', '').strip()
        patient_phone = attrs.get('patient_phone', '').strip()

        if not patient_name:
            raise serializers.ValidationError("Поле 'ФИО пациента' обязательно для заполнения.")

        if not patient_phone:
            raise serializers.ValidationError("Поле 'Телефон пациента' обязательно для заполнения.")


        phone_digits = ''.join(filter(str.isdigit, patient_phone))
        if len(phone_digits) < 5:
            raise serializers.ValidationError("Пожалуйста, введите корректный номер телефона.")

        return attrs

    def create(self, validated_data):
        patient_name = validated_data.pop('patient_name')
        patient_phone = validated_data.pop('patient_phone')
        patient_email = validated_data.pop('patient_email', '')

        appointment = Appointment.objects.create(
            patient_name=patient_name,
            patient_phone=patient_phone,
            patient_email=patient_email,
            **validated_data
        )
        return appointment