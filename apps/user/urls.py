from django.urls import path
from apps.user import my_profile
from .import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'user'

urlpatterns = [
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('my-profile/<int:user_id>/', my_profile.profile, name='my-profile'),
    path('notification/<str:username>/', views.notification, name='notification'),
    path('validate-password/', views.validate_password, name='validate_password'),
    path('notifications/mark_all_as_read/', views.mark_all_as_read, name='mark_all_as_read'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

