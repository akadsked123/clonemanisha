from django.urls import path
from .import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'faculty'

urlpatterns = [
    path('', views.faculty, name='faculty'),  
    path('faculty-workload/', views.faculty_workload, name='faculty-workload'),  
    path('assign-faculty/', views.assign_faculty, name='assign-faculty'),  
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

