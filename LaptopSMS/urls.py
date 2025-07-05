"""
URL configuration for LaptopSMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mainapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard', views.dashboard, name='dashboard'),
    path('revenueData/', views.revenueData, name="revenueData"),
    path('', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('profile/update/<int:uid>/', views.profileUpdate, name='profile_update'),
    path('profile/', views.profile, name= 'profile'),
    path('service/<int:pid>/', views.service, name='service'),
    path('serviceHistory/', views.serviceHistory, name='serviceHistory'),
    path('inward/', views.inward, name='inward'),
    path('inwardDetail/<int:pid>/', views.inwardDetail, name='inward_detail'),
    path('inwardEdit/<int:pid>/', views.inwardEdit, name='inwardEdit'),
    path('inwardHistory/', views.inwardHistory, name='inwardHistory'),
    path('serviceDetails/<int:sid>', views.serviceDetails, name='serviceDetails'),
    path('logout/', views.logout, name='logout'),
    path('keep-alive/', views.keep_alive, name='keep_alive'), 
    path('delivery/<int:did>', views.delivery, name='delivery'),
    path('team/', views.team, name='team'),
    path('team/<int:eid>/', views.team, name='team'),
    path('inactive_employee/<int:eid>/', views.inactive_employee, name='inactive_employee'),
    path('activate_employee/<int:eid>/', views.activate_employee, name='activate_employee'),
    path('deliveryHistory/', views.deliveryHistory, name="deliveryHistory"),
    path('delivery/<int:did>/', views.delivery_details, name='delivery_details'),
    path('brands/', views.brands, name="brands"),
    path('delete_brand/<int:pk>/', views.delete_brand, name='delete_brand'),




    
  

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)