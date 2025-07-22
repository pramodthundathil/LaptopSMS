from django.contrib import admin
from .models import User, Customer, ProductInward, Team, Service, Delivery, Revenue



class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customerName', 'customerEmail', 'customerMobNo', 'customerAddress')
    search_fields = ('customerName', 'customerEmail', 'customerMobNo')

class ProductInwardAdmin(admin.ModelAdmin):
    list_display = ('serialNo', 'brand', 'model', 'problem', 'remark', 'inwardDate', 'commitmentDate', 'productStatus', 'productChecked', 'customer')
    search_fields = ('serialNo', 'brand', 'model', 'customer__customerName')
    list_filter = ('brand', 'productStatus', 'productChecked')

class TeamAdmin(admin.ModelAdmin):
    list_display = ('empName', 'empEmail', 'empMobNo', 'empDOB', 'salary', 'is_active', 'position', 'empTerms')
    search_fields = ('empName', 'empEmail', 'empMobNo')
    list_filter = ('is_active', 'position')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_id', 'component', 'serviceRemark', 'serviceStatus', 'serviceCost', 'serviceDate', 'serviceTechnician', 'product')
    search_fields = ('service_id', 'component', 'serviceTechnician__empName', 'product__serialNo')
    list_filter = ('serviceStatus', 'serviceDate')

class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('product', 'service', 'customer', 'team', 'deliveryDate', 'customerSatisfaction', 'deliveredOnTime')
    search_fields = ('product__serialNo', 'service__service_id', 'customer__customerName', 'team__empName')
    list_filter = ('customerSatisfaction', 'deliveredOnTime')

class RevenueAdmin(admin.ModelAdmin):
    list_display = ('date', 'daily_revenue', 'monthly_revenue')
    search_fields = ('date',)
    list_filter = ('date',)


admin.site.register(Customer, CustomerAdmin)
admin.site.register(ProductInward, ProductInwardAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(Revenue, RevenueAdmin)
