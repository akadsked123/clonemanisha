from django.urls import path
from .import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'curriculum'

urlpatterns = [
    path('curriculum-maintenance-and-management/', views.curriculum_maintenance_and_management, name='curriculum_maintenance_and_management'),
    path('curriculum-maintenance-and-management/update/', views.edit_institute, name='edit_institute'),
    path('<slug:institute_slug>/<slug:program_slug>/view/', views.view_program_detail, name='view_program_detail'),
    path('<slug:institute_slug>/<slug:program_slug>/update/', views.update_program_detail, name='update_program_detail'),
    path('<slug:institute_slug>/<slug:program_slug>/add/', views.add_program_detail, name='add_program_detail'),

    # Program Chairperson
    path('<slug:program_slug>/', views.curriculum, name='curriculum'),
    path('<slug:institute_slug>/<slug:program_slug>/view/', views.view_program_detail, name='view_program_detail'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

