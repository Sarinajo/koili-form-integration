from django.urls import path
from django.contrib.auth import views as auth_views
from .views import open_form
from . import views

urlpatterns = [
    # Public form
    path('', open_form, name='form'),

    # Admin login
    path('admin/login/', auth_views.LoginView.as_view(template_name='core/admin_login.html'), name='admin_login'),
    path('admin/logout/', auth_views.LogoutView.as_view(next_page='admin_login'), name='admin_logout'),

    # Admin panel: list forms
    path('admin/forms/', views.admin_forms_view, name='admin_forms'),

    # Admin panel: view specific form
    path('admin/forms/<int:form_id>/', views.view_form, name='view_form'),
]
