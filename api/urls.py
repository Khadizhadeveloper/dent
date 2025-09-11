from django.urls import path
from .views import ( home,
    ServiceList, DoctorList,
    AppointmentCreate,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', home, name='home'),
    path('api/services/', ServiceList.as_view(), name='service-list'),
    path('api/doctors/', DoctorList.as_view(), name='doctor-list'),

    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/appointments/', AppointmentCreate.as_view(), name='appointment-create'),

]