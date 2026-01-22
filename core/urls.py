from django.urls import path
from . import views

urlpatterns = [
    # Public form
    path('',views.home, name='home'),
    path('form/', views.open_form, name='form'),

    # Admin authentication
    path('adminpanel/login/', views.admin_login, name='admin_login'),
    path('adminpanel/logout/', views.admin_logout, name='admin_logout'),

    # Admin panels
    path('adminpanel/forms/', views.admin_forms_view, name='admin_forms'),
    path('adminpanel/forms/processed/', views.processed_forms_view, name='processed_forms'),

    # Form actions
    path('adminpanel/forms/<int:form_id>/', views.view_form, name='view_form'),
    path('adminpanel/forms/<int:form_id>/update_status/', views.update_form_status, name='update_form_status'),
]
