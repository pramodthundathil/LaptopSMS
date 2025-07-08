from django.shortcuts import render,redirect,HttpResponse, get_object_or_404
from django.contrib.auth import authenticate,login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
import re
import datetime
from django.contrib import messages
from .models import *
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta, date
from django.db.models import Avg
from decimal import Decimal
from django.db.models import Case, When, Value, IntegerField
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm



@login_required
def dashboard(request):
    service = Service.objects.all()
    delivery = Delivery.objects.all()
    product = ProductInward.objects.all()
    product_inward_count = ProductInward.objects.count()
    service_count = Service.objects.count()
    count_employee = Team.objects.count()
    count_deliveries = Delivery.objects.count()
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()
    pendingService_count = Service.objects.filter(serviceStatus = 	"Sent For Service").count()
    servicePending = Service.objects.filter(serviceStatus = 	"Service Ongoing").count()
    serviceDone = Service.objects.filter(serviceStatus = 	"Service Done").count()
    servicePending_in = Service.objects.filter(
                serviceStatus__in=['Service Pending', 'Components Not available']).count()


    if not request.user.is_superuser:
        service = Service.objects.filter( serviceTechnician__user = request.user )
        count_deliveries = Delivery.objects.filter(service__serviceTechnician__user = request.user).count()
        service_count = service.count()
        serviceDone = serviceDone = Service.objects.filter(serviceStatus = 	"Service Done",serviceTechnician__user = request.user ).count()

    # Calculate Service count
    # serviceDone=0
    # servicePending = 0
    # for i in service:
    #     if i.serviceStatus == 'Service Done':
    #         serviceDone += 1
    #     elif i.serviceStatus == 'Service Pending' or i.serviceStatus == 'Components Not available':
    #         servicePending += 1
            
    # calculate customer satisfaction %
    satisfaction_count = Delivery.objects.filter(customerSatisfaction='Satisfied').count()
    customer_satisfaction = int((satisfaction_count / count_deliveries) * 100) if count_deliveries > 0 else 0
    
    # calculate pending services
    # pendingService_count = product_inward_count - service_count
    
    # calculate inward to service ratio
    if product_inward_count == 0:
        inward_to_service = 0  
    else:
        inward_to_service = int((serviceDone / product_inward_count) * 100)
    
    # calculate revenue
    today = now().date()
    # today = date(2024, 6, 29)
    start_of_month = today.replace(day=1)
    
    daily_revenue = 0
    monthly_revenue = 0
    
    for revenue in service:
        if revenue.serviceCost:
            if today == revenue.serviceDate:
                daily_revenue += revenue.serviceCost
                
            if start_of_month <= revenue.serviceDate <= today:
                monthly_revenue += revenue.serviceCost    
            
    Revenue.objects.update_or_create(
        date=today,
        defaults={'daily_revenue': daily_revenue, 'monthly_revenue': monthly_revenue}
    )
                
    context = {
        'product_inward_count': product_inward_count,
        'pendingService_count':pendingService_count,
        'servicePending': servicePending,
        'serviceDone': serviceDone,
        'inward_to_service': inward_to_service,
        'count_employee': count_employee,
        'count_deliveries':count_deliveries,
        'customer_satisfaction':customer_satisfaction,
        'daily_revenue': daily_revenue,
        'monthly_revenue': monthly_revenue,
        "servicePending_in":servicePending_in
        
    }
    return render(request, 'index.html', context)

def validate_password(password):
    # Password must contain at least 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special character
    # if not re.search(r"(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}", password):
    #     return False
    return True

def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        terms_accepted = request.POST.get('terms_accepted') == 'on'

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z.-]+\.[a-zA-Z]{2,}$'
        
        if (not re.match(email_pattern, email) or email.rfind(".") <= email.index('@')+2):
            messages.error(request, "Please Enter Valid Email Address")
            
        elif(not validate_password(password)):
            messages.error(request, "Password must contain at least 8 characters, one uppercase letter, one lowercase letter, and one special character")
            
        elif(password != confirm_password):
            messages.error(request, "Password Not Matched")
        elif(not terms_accepted):
            messages.error(request, "Please accept terms and conditions below the form")
        else:
            try:
                if User.objects.filter(username=email).exists():
                    messages.error(request, "This Email Already Rregistered with us...Please Login and Continue")
                else:
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        first_name=name,
                        password=password,
                        terms_accepted=terms_accepted
                    )
                    user.save()
                    messages.success(request, 'Signup Successful..Please login')
                    return redirect('login')
            except Exception as e:
                messages.error(request, "Please Enter Valid Credentials")
                
    return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Logged in as {user.first_name}")
            return redirect('/dashboard') 
        else:
            messages.error(request, "Please enter valid credentials.")
            
    return render(request, 'login.html')

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def profileUpdate(request, uid):
    user = get_object_or_404(User, id=uid)
    
    if request.method == 'POST':
        # Handle profile update
        if 'update_profile' in request.POST:
            name = request.POST.get('name')
            email = request.POST.get('email')
            profile_img = request.FILES.get('profile_img') 

            user.first_name = name
            user.email = email
            
            if profile_img:
                user.profile_img = profile_img
                print("image updated")
            user.save()

            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        
        # Handle password change
        elif 'change_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Check current password
            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
                return render(request, 'updateProfile.html', {'user': request.user})
            
            # Check if new passwords match
            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
                return render(request, 'updateProfile.html', {'user': request.user})
            
            # Check password strength (optional)
            # if len(new_password) < 8:
            #     messages.error(request, 'Password must be at least 8 characters long.')
            #     return render(request, 'updateProfile.html', {'user': request.user})
            
            # Update password
            user.set_password(new_password)
            user.save()
            
            # Keep user logged in after password change
            update_session_auth_hash(request, user)
            
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('profile')

    return render(request, 'updateProfile.html', {'user': request.user})


@login_required
def keep_alive(request):
    request.session['last_activity'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    return JsonResponse({'status': 'alive'})

@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('/')

# this function checks if user is super user or not
def is_superuser_or_staff(user):
    return user.is_superuser or user.is_staff

@login_required
def team(request, eid=None):
    if not is_superuser_or_staff(request.user):
        messages.error(request, "Access Denied: You are not authorized to view this page.")
        return redirect('dashboard')
    
    employee = None
    if eid:
        employee = get_object_or_404(Team, id=eid)
    
    if request.method == "POST":
        empName = request.POST.get('empName')
        empEmail = request.POST.get('empEmail')
        empMobNo = request.POST.get('empMobNo')
        empDOB = request.POST.get('empDOB')
        salary = request.POST.get('salary')
        position = request.POST.get('position')
        empTerms = request.POST.get('empTerms') == 'on'
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, empEmail):
            messages.error(request, "Please enter a valid email address")
            return redirect('team')
        
        if not empTerms:
            messages.error(request, "Please accept terms and conditions")
            return redirect('team')
        
        # Password validation only for new employees
        if not eid:  # Adding new employee
            if not password or not confirm_password:
                messages.error(request, "Password fields are required")
                return redirect('team')
            
            if not validate_password(password):
                messages.error(request, "Password must contain at least 8 characters, one uppercase letter, one lowercase letter, and one special character")
                return redirect('team')
            
            if password != confirm_password:
                messages.error(request, "Passwords do not match")
                return redirect('team')
        
        try:
            if eid:  # Editing existing employee
                if Team.objects.filter(empEmail=empEmail).exclude(id=eid).exists():
                    messages.error(request, "Employee with this email already exists")
                    return redirect('team')
                
                # Update employee
                employee.empName = empName
                employee.empEmail = empEmail
                employee.empMobNo = empMobNo
                employee.empDOB = empDOB
                employee.salary = salary
                employee.position = position
                employee.empTerms = empTerms
                employee.save()
                
                # Update associated user
                user = employee.user
                user.first_name = empName
                user.email = empEmail
                user.username = empEmail
                user.save()
                
                messages.success(request, 'Employee updated successfully!')
                
            else:  # Adding new employee
                if Team.objects.filter(empEmail=empEmail).exists():
                    messages.error(request, "Employee with this email already exists")
                    return redirect('team')
                
                if User.objects.filter(username=empEmail).exists():
                    messages.error(request, "This email is already registered")
                    return redirect('team')
                
                # Create user
                user = User.objects.create_user(
                    username=empEmail,
                    email=empEmail,
                    first_name=empName,
                    password=password
                )
                
                # Create employee
                employee = Team.objects.create(
                    user=user,
                    empName=empName,
                    empEmail=empEmail,
                    empMobNo=empMobNo,
                    empDOB=empDOB,
                    salary=salary,
                    position=position,
                    empTerms=empTerms
                )
                
                messages.success(request, 'Employee added successfully!')
                
        except Exception as e:
            messages.error(request, f"Error processing request: {str(e)}")
            return redirect('team')
        
        return redirect('team')
    
    # Get all employees
    employees = Team.objects.all().order_by('-id')
    
    context = {
        'employees': employees,
        'employee': employee,
    }
    
    return render(request, 'team.html', context)


@login_required
def inactive_employee(request, eid):
    emp = get_object_or_404(Team, id=eid)
    emp.is_active = False
    emp.user.is_active = False
    emp.save()
    messages.success(request, 'Employee marked as inactive successfully')
    return redirect('team')

@login_required
def activate_employee(request, eid):
    emp = get_object_or_404(Team, id=eid)
    emp.is_active = True
    emp.user.is_active = True
    emp.save()
    messages.success(request, 'Employee activated successfully')
    return redirect('team')

@login_required
def inward(request):
    technician_positions = ['Laptop Technician', 'Computer Technician', 'Chip-level Technician']
    technicians = Team.objects.filter(position__in=technician_positions, is_active=True)
    brands = Brands.objects.all()
    if request.method == "POST":
        serialNo = request.POST.get('serialNo')
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        problem = request.POST.get('problem')
        remark = request.POST.get('remark')
        commitmentDate = request.POST.get('commitmentDate')
        productStatus = request.POST.get('productStatus')
        productChecked = request.POST.get('productChecked', 'off') == 'on'
        
        customerName = request.POST.get('customerName')
        customerEmail = request.POST.get('customerEmail')
        customerMobNo = request.POST.get('customerMobNo')
        customerAddress = request.POST.get('customerAddress')

        technician = request.POST.get('technician') 
        try: 
            serviceTechnician = get_object_or_404(Team, id=technician)
        except:
            serviceTechnician = None
        customer = Customer(
            customerName = customerName,
            customerEmail = customerEmail,
            customerMobNo = customerMobNo,
            customerAddress = customerAddress,
        )
        customer.save()
        
        productInward = ProductInward(
            serialNo = serialNo,
            brand = brand,
            model = model,
            problem = problem,
            remark = remark,
            commitmentDate = commitmentDate,
            productStatus = productStatus,
            productChecked = productChecked,
            customer = customer,
        )
        productInward.save()

        if productStatus == "In Service":
            service = Service(
                
                product=productInward,
                serviceTechnician=serviceTechnician,
                serviceStatus = "Sent For Service"
            )
        
            service.save()
            messages.success(request, "Product added for service")
            return redirect('/serviceHistory')

        messages.success(request, "Product Inwarded")
        return redirect('/inwardHistory')
    return render(request, 'inward.html',{"technicians":technicians,"brands":brands})

@login_required
def inwardHistory(request):
    product_inward = ProductInward.objects.all().order_by(
        Case(
            When(productStatus='Delivered', then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        ),
        '-id'
    )
        
    context = {
        'product_inward': product_inward,
    }
    return render(request, 'inwardHistory.html', context)

@login_required
def inwardDetail(request,pid):
    product = get_object_or_404(ProductInward, id=pid)   
    context = {
        'product': product,
    }
    return render(request, 'inwardDetail.html', context)

@login_required
def inwardEdit(request,pid):
    technician_positions = ['Laptop Technician', 'Computer Technician', 'Chip-level Technician']
    technicians = Team.objects.filter(position__in=technician_positions, is_active=True)
    brands = Brands.objects.all()
    product = get_object_or_404(ProductInward, id=pid)
    
    if request.method == "POST":
        product.serialNo = request.POST.get('serialNo')
        product.brand = request.POST.get('brand')
        product.model = request.POST.get('model')
        product.problem = request.POST.get('problem')
        product.remark = request.POST.get('remark')
        product.commitmentDate = request.POST.get('commitmentDate')
        product.productStatus = request.POST.get('productStatus')
        product.productChecked = request.POST.get('productChecked') == 'on'
        
        customer = product.customer
        if customer:
            customer.customerName = request.POST.get('customerName')
            customer.customerEmail = request.POST.get('customerEmail')
            customer.customerMobNo = request.POST.get('customerMobNo')
            customer.customerAddress = request.POST.get('customerAddress')
            customer.save()
        else:
            customer = Customer(
                customerName = request.POST.get('customerName'),
                customerEmail = request.POST.get('customerEmail'),
                customerMobNo = request.POST.get('customerMobNo'),
                customerAddress = request.POST.get('customerAddress'),
            )
            customer.save()
            product.customer = customer
        
        product.save()
        messages.success(request, "Inward details updated successfully.")
        return redirect('inward_detail', pid=product.id)
            
    context = {
        'product': product,
        "technicians":technicians,
        "brands":brands
    }
    return render(request, 'inwardEdit.html', context)

from django.db import transaction

@login_required
def service(request, pid):
    product = get_object_or_404(ProductInward, id=pid)
    service = Service.objects.filter(product=product).first()
    
    technician_positions = ['Laptop Technician', 'Computer Technician', 'Chip-level Technician']
    technicians = Team.objects.filter(position__in=technician_positions, is_active=True)
    
    # Get all inventory items for component selection
    inventories = Inventory.objects.filter(stock__gt=0).order_by('name')
    
    if request.method == "POST":
        serviceRemark = request.POST.get('serviceRemark')
        serviceStatus = request.POST.get('serviceStatus')
        serviceCost = request.POST.get('serviceCost') or 0
        serviceTechnician_id = request.POST.get('serviceTechnician')
        component_inventory_data = request.POST.getlist('component_inventory')
        
        # Get technician
        serviceTechnician = None
        if serviceTechnician_id:
            serviceTechnician = get_object_or_404(Team, id=serviceTechnician_id)
        
        # Use transaction to ensure data consistency
        with transaction.atomic():
            # Create or update service
            if service:
                # Store old components to restore stock if needed
                old_components = {}
                for comp in service.component_inventory.all():
                    # If you have a through model with quantity, get it here
                    # For now, assuming quantity of 1 per component
                    old_components[comp.id] = 1
                
                # Clear old component relationships
                service.component_inventory.clear()
                
                # Update service fields
                service.serviceRemark = serviceRemark
                service.serviceStatus = serviceStatus
                service.serviceCost = serviceCost
                service.serviceTechnician = serviceTechnician
            else:
                # Create new service
                service = Service(
                    serviceRemark=serviceRemark,
                    serviceStatus=serviceStatus,
                    product=product,
                    serviceCost=serviceCost,
                    serviceTechnician=serviceTechnician
                )
                old_components = {}
            
            service.save()
            
            # Process component inventory
            selected_components = {}
            component_names = []
            
            for item in component_inventory_data:
                if ':' in item:
                    comp_id, quantity = item.split(':')
                    comp_id = int(comp_id)
                    quantity = int(quantity)
                    
                    try:
                        inventory_item = Inventory.objects.get(id=comp_id)
                        
                        # Check if enough stock is available
                        required_stock = quantity
                        if comp_id in old_components:
                            # If this component was used before, add back its old quantity
                            required_stock -= old_components[comp_id]
                        
                        if inventory_item.stock >= required_stock:
                            # Add to service
                            service.component_inventory.add(inventory_item)
                            selected_components[comp_id] = quantity
                            component_names.append(f"{inventory_item.name} (x{quantity})")
                            
                            # Update stock - decrease by the difference
                            inventory_item.stock -= required_stock
                            inventory_item.save()
                        else:
                            # Rollback transaction if not enough stock
                            raise ValueError(f"Not enough stock for {inventory_item.name}. Available: {inventory_item.stock}, Required: {required_stock}")
                    
                    except Inventory.DoesNotExist:
                        raise ValueError(f"Inventory item with ID {comp_id} not found")
            
            # Restore stock for components that were removed
            for old_comp_id, old_quantity in old_components.items():
                if old_comp_id not in selected_components:
                    # This component was removed, restore its stock
                    try:
                        inventory_item = Inventory.objects.get(id=old_comp_id)
                        inventory_item.stock += old_quantity
                        inventory_item.save()
                    except Inventory.DoesNotExist:
                        pass
            
            # Update component field with component names
            service.component = ', '.join(component_names) if component_names else None
            service.save()
            
            # Update product details
            product.problem = request.POST.get('problem')
            product.remark = request.POST.get('remark')
            product.productStatus = 'In Service'
            product.save()
            
            messages.success(request, "Service Status Updated Successfully")
            return redirect('/serviceHistory')
    

    
    context = {
        'product': product,
        'service': service,
        'technicians': technicians,
        'inventories': inventories,
    }
    
    return render(request, 'serviceForm.html', context)

@login_required
def serviceHistory(request):
    if request.user.is_superuser:
        service = Service.objects.all().order_by('-id')
    else:
        service = Service.objects.filter(serviceTechnician__user = request.user).order_by('-id')

    context = {
        'service' : service,
    }
    return render(request, 'serviceHistory.html', context)

@login_required
def serviceDetails(request, sid):
    service = get_object_or_404(Service, id=sid)
    
    context = {
        'service' : service,
    }
    
    return render(request, 'serviceDetails.html', context)


@login_required
def update_service_cost(request,pk ):

    service  = get_object_or_404(Service, id = pk)
    if request.method == "POST":
        if service:
            service.serviceCost = request.POST['service_cost']
            service.save()
            messages.success(request,"Service Cost Updated")
            return redirect("serviceDetails", sid = pk)
        else:
            messages.success(request,"No service")
            return redirect("serviceDetails", sid = pk)


def delivery(request, did):
    service = get_object_or_404(Service, id=did)
    product = get_object_or_404(ProductInward, id= service.product.id)
    customer = get_object_or_404(Customer, id=product.id)
    
    if request.method == 'POST':
        customerSatisfaction = request.POST.get('customerSatisfaction')
        deliveredOnTime = request.POST.get('deliveredOnTime')
        
        delivery = Delivery.objects.create(
            service=service,
            customerSatisfaction=customerSatisfaction,
            deliveredOnTime=deliveredOnTime,
            customer = customer,
            product = product

        )
        delivery.save()
        
        product.productStatus = 'Delivered'
        product.save()
        
        service.serviceStatus = 'Service Done'
        service.save()
        
        messages.success(request, 'Product Delivered Successfully')
        return redirect('deliveryHistory')
    
    context = {
        'service':service,
        'product':product,
        'customer':customer
    }
    
    return render(request, 'deliveryForm.html', context)


def deliveryHistory(request):
    services = Service.objects.all()
    if request.user.is_superuser:
        deliveries = Delivery.objects.all().order_by('-id')

    else:
        deliveries = Delivery.objects.filter(service__serviceTechnician__user = request.user).order_by('-id')

    
    context = {
        'services': services,
        'deliveries': deliveries
    }
    
    return render(request, 'deliveryHistory.html', context)


def delivery_details(request, did):
    delivery = get_object_or_404(Delivery, id=did)
    context = {
        'delivery': delivery,
    }
    return render(request, 'deliveryDetails.html', context)

# views.py

from django.shortcuts import render
from django.utils.timezone import now
from .models import Revenue
from django.db.models.functions import ExtractMonth, ExtractYear

@login_required
def revenueData(request):
    # Get the current year and month
    current_year = now().year
    current_month = now().month
    
    # Get year and month from request parameters, default to current year and month
    selected_year = int(request.GET.get('year', current_year))
    selected_month = int(request.GET.get('month', current_month))
    
    # Filter revenues by selected year and month
    revenues = Revenue.objects.annotate(
        year=ExtractYear('date'),
        month=ExtractMonth('date')
    ).filter(year=selected_year, month=selected_month)
    
    # Calculate total monthly revenue
    total_monthly_revenue = revenues.aggregate(total=models.Sum('daily_revenue'))['total'] or 0
    
    # Get list of years and months for the filter dropdowns
    years = Revenue.objects.dates('date', 'year')
    months = Revenue.objects.dates('date', 'month')
    
    context = {
        'revenues': revenues,
        'total_monthly_revenue': total_monthly_revenue,
        'years': years,
        'months': months,
        'selected_year': selected_year,
        'selected_month': selected_month,
    }
    return render(request, 'revenueData.html', context)


# new edits 
@login_required
def brands(request):
    brand = Brands.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        if Brands.objects.filter(name = name).exists():
            messages.info(request,"This brand is already exists in database")
            return redirect("brands")
        else:
            value = Brands.objects.create(name= name)
            value.save()
            messages.success(request,"Brand added in Database")
            return redirect(brands)
    context = {
        "brand":brand
    }
    return render(request,"brands.html",context)


@login_required
def delete_brand(request, pk):
    brand = get_object_or_404(Brands, id = pk)
    brand.delete()
    messages.success(request,"Brand Deleted....")
    return redirect("brands")



from django.http import JsonResponse
from django.views.decorators.http import require_POST
# notifications 
def notifications(request):
    """Display all notifications for the current user"""
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count
    }
    return render(request,"notification.html",context)


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    else:
        messages.success(request, 'Notification marked as read')
        return redirect('notifications')

@login_required
def get_notifications_count(request):
    """Get unread notifications count via AJAX"""
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})

@login_required
def get_latest_notifications(request):
    """Get latest notifications for real-time updates"""
    notifications = Notification.objects.filter(
        user=request.user, 
        is_read=False
    )[:5]  # Get latest 5 unread notifications
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'service_id': notification.service.service_id if notification.service else None
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': len(notifications_data)
    })


def notification_mark_read(request,pk):
    notification = get_object_or_404(Notification, id = pk)
    notification.is_read = True 
    notification.save()
    return redirect("serviceDetails", sid = notification.service.id )


# tax calculations

from .models import Tax
from .forms import TaxForm, InventoryForm

@login_required(login_url='signin')
def AddTax(request):
    if request.method == "POST":
        name = request.POST.get('name')
        tax_rate = request.POST.get('tax')
        tax = Tax.objects.create(tax_name = name,tax_percentage = tax_rate )
        tax.save()
        messages.success(request,'Tax Value Added Success')
        return redirect("ListTax")
    return render(request,"add-tax-slab.html")

@login_required(login_url='signin')
def ListTax(request):
    tax = Tax.objects.all()
    context = {
        "tax":tax
    }
    return render(request,"list-tax.html",context)

@login_required(login_url="signin")
def delete_tax(request,pk):
    tax = get_object_or_404(Tax,pk=pk)
    tax.delete()
    messages.success(request,'Tax Value Deleted Success')
    return redirect("ListTax")

@login_required(login_url="signin")
def tax_single_update(request,pk):
    tax = get_object_or_404(Tax,pk=pk)
    form = TaxForm(instance = tax)
    if request.method == "POST":
        form = TaxForm(request.POST,instance = tax)
        if form.is_valid():
            tax = form.save()
            tax.save()
            messages.success(request,'Tax Value Updated Success')
            return redirect("ListTax")
    return render(request,"tax-single.html",{"form":form})


@login_required
def inventory(request):
    inventories = Inventory.objects.all().order_by("-id")
    form = InventoryForm()
    
    if request.method == "POST":
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Inventory added successfully!")
            return redirect("inventory")
        else:
            messages.error(request, "Please correct the errors below.")
    
    return render(request, 'inventory.html', {
        "inventories": inventories,
        "form": form
    })

@login_required
def edit_inventory(request, inventory_id):
    inventory = get_object_or_404(Inventory, id=inventory_id)
    form = InventoryForm( instance=inventory)
    if request.method == "POST":
        form = InventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            messages.success(request, "Inventory updated successfully!")
            return redirect("inventory")
        else:
            messages.error(request, "Please correct the errors below.")
    
    return render(request,"inventory_single.html",{"form":form})

@login_required
def delete_inventory(request, inventory_id):
    inventory = get_object_or_404(Inventory, id=inventory_id)
    inventory_name = inventory.name
    inventory.delete()
    messages.success(request, f"Inventory item '{inventory_name}' has been deleted successfully!")
    return redirect("inventory")



# invoice 

def generate_invoice_html(request, delivery_id):
    """Generate HTML invoice for a delivery"""
    delivery = get_object_or_404(Delivery, id=delivery_id)
    
    # Calculate total cost
    total_cost = 0
    if delivery.service:
        total_cost = delivery.service.serviceCost
    
    # Generate invoice number
    invoice_number = f"INV-{delivery.id:06d}"
    
    context = {
        'delivery': delivery,
        'invoice_number': invoice_number,
        'invoice_date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'total_cost': total_cost,
    }
    
    return render(request, 'invoice.html', context)


# analytics 

from django.shortcuts import render
from django.db.models import Count, Sum, Q, Avg
from django.db.models.functions import TruncMonth, TruncYear
from django.utils import timezone
from datetime import datetime, timedelta
import json
from .models import (
    ProductInward, Service, Delivery, Customer, Team, 
    Revenue, Inventory, Notification
)

def analytics_dashboard(request):
    # Get current date
    current_date = timezone.now()
    
    # Get selected month and year from request (default to current)
    selected_month = int(request.GET.get('month', current_date.month))
    selected_year = int(request.GET.get('year', current_date.year))
    
    # Create date range for selected month
    start_date = datetime(selected_year, selected_month, 1)
    if selected_month == 12:
        end_date = datetime(selected_year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(selected_year, selected_month + 1, 1) - timedelta(days=1)
    
    # 1. Product Inward Analytics
    products_inward = ProductInward.objects.filter(
        inwardDate__range=[start_date, end_date]
    )
    
    total_products_inward = products_inward.count()
    products_checked = products_inward.filter(productChecked=True).count()
    products_pending = products_inward.filter(productChecked=False).count()
    
    # Product status distribution
    product_status_data = products_inward.values('productStatus').annotate(
        count=Count('id')
    ).order_by('productStatus')
    
    # Brand-wise product distribution
    brand_data = products_inward.values('brand').annotate(
        count=Count('id')
    ).order_by('-count')[:10]  # Top 10 brands
    
    # 2. Service Analytics
    services = Service.objects.filter(
        serviceDate__range=[start_date, end_date]
    )
    
    total_services = services.count()
    total_service_cost = services.aggregate(Sum('serviceCost'))['serviceCost__sum'] or 0
    avg_service_cost = services.aggregate(Avg('serviceCost'))['serviceCost__avg'] or 0
    
    # Service status distribution
    service_status_data = services.values('serviceStatus').annotate(
        count=Count('id')
    ).order_by('serviceStatus')
    
    # Technician performance
    technician_performance = services.values(
        'serviceTechnician__empName'
    ).annotate(
        services_count=Count('id'),
        total_cost=Sum('serviceCost')
    ).order_by('-services_count')
    
    # 3. Delivery Analytics
    deliveries = Delivery.objects.filter(
        deliveryDate__range=[start_date, end_date]
    )
    
    total_deliveries = deliveries.count()
    on_time_deliveries = deliveries.filter(deliveredOnTime='Yes').count()
    
    # Customer satisfaction
    satisfaction_data = deliveries.values('customerSatisfaction').annotate(
        count=Count('id')
    ).order_by('customerSatisfaction')
    
    # 4. Revenue Analytics
    revenue_data = Revenue.objects.filter(
        date__range=[start_date, end_date]
    )
    
    total_monthly_revenue = revenue_data.aggregate(
        Sum('daily_revenue')
    )['daily_revenue__sum'] or 0
    
    # Daily revenue chart data
    daily_revenue_chart = revenue_data.values('date', 'daily_revenue').order_by('date')
    
    # 5. Customer Analytics
    customers = Customer.objects.filter(
        product_inward__inwardDate__range=[start_date, end_date]
    ).distinct()
    
    total_customers = customers.count()
    repeat_customers = customers.filter(
        product_inward__inwardDate__lt=start_date
    ).count()
    
    # 6. Team Analytics
    active_team_members = Team.objects.filter(is_active=True).count()
    
    # Position-wise team distribution
    position_data = Team.objects.filter(is_active=True).values('position').annotate(
        count=Count('id')
    ).order_by('position')
    
    # 7. Inventory Analytics
    low_stock_items = Inventory.objects.filter(stock__lt=10).count()
    total_inventory_value = Inventory.objects.aggregate(
        total_value=Sum('rate_of_purchase')
    )['total_value'] or 0
    
    # 8. Monthly comparison data (last 6 months)
    six_months_ago = current_date - timedelta(days=180)
    monthly_comparison = ProductInward.objects.filter(
        inwardDate__gte=six_months_ago
    ).annotate(
        month=TruncMonth('inwardDate')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # 9. Notifications count
    unread_notifications = Notification.objects.filter(
        is_read=False,
        created_at__range=[start_date, end_date]
    ).count()
    
    # Prepare chart data for JavaScript
    chart_data = {
        'productStatus': list(product_status_data),
        'brandData': list(brand_data),
        'serviceStatus': list(service_status_data),
        'satisfactionData': list(satisfaction_data),
        'positionData': list(position_data),
        'monthlyComparison': [
            {
                'month': item['month'].strftime('%Y-%m'),
                'count': item['count']
            } for item in monthly_comparison
        ],
        'dailyRevenue': [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'revenue': float(item['daily_revenue'])
            } for item in daily_revenue_chart
        ]
    }
    
    context = {
        'selected_month': selected_month,
        'selected_year': selected_year,
        'current_date': current_date,
        
        # Summary cards data
        'total_products_inward': total_products_inward,
        'products_checked': products_checked,
        'products_pending': products_pending,
        'total_services': total_services,
        'total_service_cost': total_service_cost,
        'avg_service_cost': avg_service_cost,
        'total_deliveries': total_deliveries,
        'on_time_deliveries': on_time_deliveries,
        'total_monthly_revenue': total_monthly_revenue,
        'total_customers': total_customers,
        'repeat_customers': repeat_customers,
        'active_team_members': active_team_members,
        'low_stock_items': low_stock_items,
        'total_inventory_value': total_inventory_value,
        'unread_notifications': unread_notifications,
        
        # Table data
        'technician_performance': technician_performance,
        'brand_data': brand_data,
        
        # Chart data
        'chart_data': json.dumps(chart_data),
        
        # Additional metrics
        'on_time_percentage': round((on_time_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0, 2),
        'check_percentage': round((products_checked / total_products_inward * 100) if total_products_inward > 0 else 0, 2),
    }
    
    return render(request, 'analytics_dashboard.html', context)
