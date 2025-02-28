from django.urls import path
from .import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'programs'

urlpatterns = [
     path('', views.programs, name='programs'),
     path('curriculum-version/', views.curriculum_version, name='curriculum-version'),
     path('curriculum-version/courses/', views.courses, name='courses'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



