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

@login_required
def dashboard(request):
    service = Service.objects.all()
    delivery = Delivery.objects.all()
    product = ProductInward.objects.all()
    product_inward_count = ProductInward.objects.count()
    service_count = Service.objects.count()
    count_employee = Team.objects.count()
    count_deliveries = Delivery.objects.count()
    
    # Calculate Service count
    serviceDone=0
    servicePending = 0
    for i in service:
        if i.serviceStatus == 'Service Done':
            serviceDone += 1
        elif i.serviceStatus == 'Service Pending' or i.serviceStatus == 'Components Not available':
            servicePending += 1
            
    # calculate customer satisfaction %
    satisfaction_count = Delivery.objects.filter(customerSatisfaction='Satisfied').count()
    customer_satisfaction = int((satisfaction_count / count_deliveries) * 100) if count_deliveries > 0 else 0
    
    # calculate pending services
    pendingService_count = product_inward_count - service_count
    
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
    }
    return render(request, 'index.html', context)

def validate_password(password):
    # Password must contain at least 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special character
    if not re.search(r"(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}", password):
        return False
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
    product_inward = ProductInward.objects.all().order_by('-id')
    
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
    }
    return render(request, 'inwardEdit.html', context)

@login_required
def service(request, pid):
    product = get_object_or_404(ProductInward, id=pid)
    service = Service.objects.filter(product=product).first()
    
    technician_positions = ['Laptop Technician', 'Computer Technician', 'Chip-level Technician']
    technicians = Team.objects.filter(position__in=technician_positions, is_active=True)
    print(technicians,"-------------------------------------")
    if request.method == "POST":
        component = request.POST.get('component')
        serviceRemark = request.POST.get('serviceRemark')
        serviceStatus = request.POST.get('serviceStatus')
        serviceCost = request.POST.get('serviceCost') or 0
        serviceTechnician_id = request.POST.get('serviceTechnician')
        
        serviceTechnician = get_object_or_404(Team, id=serviceTechnician_id)
        
        if service:
            service.component = component
            service.serviceRemark = serviceRemark
            service.serviceStatus = serviceStatus
            service.serviceCost = serviceCost
            service.serviceTechnician = serviceTechnician
        else:
            service = Service(
                component=component,
                serviceRemark=serviceRemark,
                serviceStatus=serviceStatus,
                product=product,
                serviceCost=serviceCost,
                serviceTechnician=serviceTechnician
            )
        
        service.save()
        
        product.problem = request.POST.get('problem')
        product.remark = request.POST.get('remark')
        product.productStatus = 'In Service'
        product.save()
        
        messages.success(request, "Service Status Updated")
        return redirect('/serviceHistory')

    context = {
        'product': product,
        'service': service,
        'technicians': technicians,
    }
    
    return render(request, 'serviceForm.html', context)

@login_required
def serviceHistory(request):
    service = Service.objects.all().order_by('-id')
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
            deliveredOnTime=deliveredOnTime
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
    deliveries = Delivery.objects.all().order_by('-id')
    
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