from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .views import CustomLoginView

from django.contrib import admin
urlpatterns = [
    
    path('admin/', admin.site.urls), 
    path('', views.home, name=""),
    path('register',views.register, name = "register"),
    path('login',CustomLoginView.as_view(),name = "login"),
    path('role-selection/', views.role_selection_view, name='role_selection'),
    path('role-based-page/', views.role_based_page, name='role_based_page'),
    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('logout',views.logout,name="logout"),
    path('dashboard/',views.role_based_page,name='dashboard'),
    path('create',views.create,name="create"),
    path('upload/', views.upload, name='upload'),
    path('update/<int:pk>',views.update,name="update"),
    path('record/<int:pk>',views.record,name="record"),
    path('delete/<int:pk>',views.delete,name="delete"),
    path('about/', views.about, name='about'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)