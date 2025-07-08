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
    path('update_service_cost/<int:pk>', views.update_service_cost, name='update_service_cost'),
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
# notification system

    path("notifications",views.notifications,name="notifications"),
     path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/count/', views.get_notifications_count, name='notifications_count'),
    path('notifications/latest/', views.get_latest_notifications, name='latest_notifications'),

    path("notification_mark_read/<int:pk>",views.notification_mark_read,name="notification_mark_read"),

    # tax calculations 
    path("AddTax/", views.AddTax, name="AddTax"),
    path("ListTax/", views.ListTax, name="ListTax"),
    path("delete_tax/<int:pk>", views.delete_tax, name="delete_tax"),
    path("tax_single_update/<int:pk>", views.tax_single_update, name="tax_single_update"),

    # inventory
    path("inventory",views.inventory,name="inventory"),
    path('edit_inventory/<int:inventory_id>/', views.edit_inventory, name='edit_inventory'),
    path('delete_inventory/<int:inventory_id>/', views.delete_inventory, name='delete_inventory'),

    # invoice
    path("generate_invoice_html/<int:delivery_id>",views.generate_invoice_html,name="generate_invoice_html"),

    # analytics
    path('analytics_dashboard', views.analytics_dashboard, name='analytics_dashboard'),
    
  

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)