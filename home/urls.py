from django.urls import path 

from .import views 

urlpatterns =[
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

     # vendor management ......................................

    path("add_vendor",views.add_vendor,name="add_vendor"),
    path("add_vendor_form_purchase/<int:pk>",views.add_vendor_form_purchase,name="add_vendor_form_purchase"),
    path("list_vendor",views.list_vendor,name="list_vendor"),
    path("update_vendor/<int:pk>",views.update_vendor,name="update_vendor"),
    path("delete_vendor/<int:pk>",views.delete_vendor,name="delete_vendor"),
    path("delete_bulk_supplier",views.delete_bulk_supplier,name="delete_bulk_supplier"),

    # inventory
    path("inventory",views.inventory,name="inventory"),
    path("add_inventory_form_purchase/<int:pk>",views.add_inventory_form_purchase,name="add_inventory_form_purchase"),
    path('add_inventory',views.add_inventory,name="add_inventory"),
    path('edit_inventory/<int:inventory_id>/', views.edit_inventory, name='edit_inventory'),
    path('delete_inventory/<int:inventory_id>/', views.delete_inventory, name='delete_inventory'),

    # invoice
    path("generate_invoice_html/<int:delivery_id>",views.generate_invoice_html,name="generate_invoice_html"),

    # analytics
    path('analytics_dashboard', views.analytics_dashboard, name='analytics_dashboard'),

    # download DB
    path("download_db",views.download_db,name="download_db"),

    # purchases 
    

    path("purchase",views.purchase,name="purchase"),
    path("delete_bulk_purchase",views.delete_bulk_purchase,name="delete_bulk_purchase"),
    path("add_purchase",views.add_purchase,name="add_purchase"),
    # path("purchase_from_order/<int:order_id>",views.purchase_from_order,name="purchase_from_order"),
    path("edit_purchase/<int:pk>",views.edit_purchase,name="edit_purchase"),
    path("deletepurchase/<int:pk>",views.deletepurchase,name="deletepurchase"),
    path("change_purchase_date/<int:pk>",views.change_purchase_date,name="change_purchase_date"),
    path("add_purchase_item/<int:pk>",views.add_purchase_item,name="add_purchase_item"),
    # path("update_supplier_to_purchase",views.update_supplier_to_purchase,name="update_supplier_to_purchase"),
    path("update_purchase_item/<int:order_id>",views.update_purchase_item,name="update_purchase_item"),
    path("update_purchase_payment/<int:order_id>",views.update_purchase_payment,name="update_purchase_payment"),
    path("payment_given_in_expense_purchase",views.payment_given_in_expense_purchase,name="payment_given_in_expense_purchase"),
    path("add_bill_discount_to_purchase/<int:pk>",views.add_bill_discount_to_purchase,name="add_bill_discount_to_purchase"),
    path("delete_purchase_item/<int:pk>",views.delete_purchase_item,name="delete_purchase_item"),
    path("update_supplier_to_purchase",views.update_supplier_to_purchase,name="update_supplier_to_purchase"),
    path('update_data_on_purchase/<int:pk>',views.update_data_on_purchase,name="update_data_on_purchase"),
   
    path('vendor/<int:pk>/payments/', views.view_vendor_payments, name='view_vendor_payments'),
    path('payment/make/<int:purchase_id>/', views.make_payment, name='make_payment'),
    path('vendor/<int:vendor_id>/payment-summary/', views.vendor_payment_summary, name='vendor_payment_summary'),
    path('vendor/<int:vendor_id>/payment-history/', views.payment_history, name='payment_history'),
    path('payment/make/<int:purchase_id>/purchase', views.make_payment_from_purchase, name='make_payment_from_purchase'),


]