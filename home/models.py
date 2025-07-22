from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
import random
import string

from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    terms_accepted = models.BooleanField(default=True)
    profile_img = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    def __str__(self):
        return self.username


class Brands(models.Model):
    name = models.CharField(max_length=20)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.name)
    
class Customer(models.Model):
    customerName = models.CharField(max_length=100)
    customerEmail = models.EmailField()
    customerMobNo = models.BigIntegerField()
    customerAddress = models.TextField()
    
    def __str__(self):
        return self.customerName

class Vendor(models.Model):
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(
        max_length=15,
        # validators=[RegexValidator(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )
    gst_number = models.CharField(max_length=15, validators=[MinLengthValidator(15), MaxLengthValidator(15)], null=True, blank=True)
    city = models.CharField(max_length=255,blank=True, null=True)
    state = models.CharField(max_length=255,blank=True, null=True)
    country = models.CharField(max_length=255,blank=True, null=True)
    pincode = models.CharField(max_length=10,blank=True, null=True)
    contact_info = models.TextField(blank=True, null=True)
    supply_product = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name )




    
# Product Inward Model
class ProductInward(models.Model):
    serialNo = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    problem = models.TextField()
    remark = models.TextField()
    inwardDate = models.DateTimeField(auto_now_add=True)
    commitmentDate = models.DateField()
    productStatus = models.CharField(max_length=30)
    productChecked = models.BooleanField(default=False)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True ,related_name='product_inward')

    def __str__(self):
        return self.serialNo

class Team(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    empName = models.CharField(max_length=100)
    empEmail = models.EmailField()
    empMobNo = models.BigIntegerField()
    empDOB = models.DateField()
    salary = models.FloatField()
    
    is_active = models.BooleanField(default=True)
    
    position = models.CharField(max_length=30, choices=[
        ('Laptop Technician', 'Laptop Technician'),
        ('Computer Technician', 'Computer Technician'),
        ('Chip-level Technician', 'Chip-level Technician'),
        ('Manager', 'Manager'),
        ('HR', 'HR'),
        ('Other Staff', 'Other Staff')], null=False)
    empTerms = models.BooleanField(default=False)
    
    def delete(self, *args, **kwargs):
        self.is_active = False
        self.user.is_active = False
        self.save()
        
    def __str__(self):
        return str(self.empName) + str(f' ({self.position})')
    
#Service model
class Service(models.Model):
    service_id = models.CharField(max_length=7, unique=True, editable=False)
    component = models.CharField(max_length=100, null=True)
    component_inventory = models.ManyToManyField("Inventory")
    serviceRemark = models.CharField(max_length=100, null=True,blank=True)
    serviceStatus = models.CharField(max_length=30, null=True,blank=True)
    serviceCost = models.FloatField(default=0)
    serviceDate = models.DateField(auto_now=True)
    
    serviceTechnician = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='serviceTechnician')
    product = models.ForeignKey(ProductInward, on_delete=models.SET_NULL, null=True ,related_name='service')
    
    def __str__(self):
        return f"Service ID: {self.service_id}"
    
    def save(self, *args, **kwargs):
        if not self.service_id:
            self.service_id = self.generate_unique_id()
        super().save(*args, **kwargs)

    def generate_unique_id(self):
        while True:
            random_digits = ''.join(random.choices(string.digits, k=4))
            service_id = f"SER{random_digits}"
            if not Service.objects.filter(service_id=service_id).exists():
                return service_id


class Delivery(models.Model):
    product = models.ForeignKey(ProductInward, on_delete=models.SET_NULL, null=True ,related_name='product')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True ,related_name='service')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True ,related_name='Customer')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True ,related_name='team')
    
    deliveryDate = models.DateTimeField(auto_now_add=True)
    
    customerSatisfaction = models.CharField(max_length=20, choices=[
        ('Satisfied', 'Satisfied'),
        ('Neutral', 'Neutral'),
        ('Not Satisfied', 'Not Satisfied')
    ], null=True, blank=True)
    
    deliveredOnTime = models.CharField(max_length=20, choices=[
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], null=True, blank=True)
    
# Revenue Data
class Revenue(models.Model):
    date = models.DateField()
    daily_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monthly_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)


# Add this Notification model
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    service = models.ForeignKey('Service', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
class Tax(models.Model):
    tax_name = models.CharField(max_length=20)
    tax_percentage = models.FloatField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}  {} %'.format(str(self.tax_name),(self.tax_percentage))



class Inventory(models.Model):
    inventory_code = models.CharField(max_length=8, unique=True, editable=False)
    name = models.CharField(max_length=200)
    brand_name = models.CharField(max_length=100)
    base_product = models.CharField(
        max_length=100,
        choices=(
            ("Laptop", "Laptop"),
            ("Desktop", "Desktop"),
            ("Monitor Part", "Monitor Part"),
            ("Keyboard", "Keyboard"),
            ("Motherboard", "Motherboard"),
            ("RAM", "RAM"),
            ("Hard Disk", "Hard Disk"),
            ("SSD", "SSD"),
            ("Battery", "Battery"),
            ("Charger", "Charger"),
            ("Screen", "Screen"),
            ("Mouse", "Mouse"),
            ("Printer", "Printer"),
            ("Other", "Other"),
            )
        )
    value = models.CharField(max_length=100, help_text="Values like 16Gb, 500SSD", null=True, blank=True)
    rate_of_purchase = models.FloatField(null=True, blank=True)
    stock = models.IntegerField()
    date_added= models.DateField(auto_now_add=True)

    date_created = models.DateField(auto_now=True)
    # Additional fields
    price_before_tax = models.FloatField(null=True, blank=True, default=0)
    tax_amount = models.FloatField(null=True, blank=True,)


    
    def save(self, *args, **kwargs):
        if not self.inventory_code:
            while True:
                code = f"IN{''.join(random.choices(string.digits, k=6))}"
                if not Inventory.objects.filter(inventory_code=code).exists():
                    self.inventory_code = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name)



class Purchase(models.Model):
    PURCHASE_TYPES = [
        ('Credit', 'Credit'),
        ('Cash', 'Cash'),
        
    ]
    PAYMENT_STATUS = (
        ("UNPAID","UNPAID"),
        ("PAID","PAID"),
        ("PARTIALLY","PARTIALLY")
    )
    
    purchase_type = models.CharField(max_length=20, choices=PURCHASE_TYPES)
    bill_date = models.DateTimeField(auto_now_add=True)
    supplier = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name='purchase_supply')
    payment_terms = models.CharField(help_text='Number of days, Credit Period',max_length=255, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    place_of_supply = models.CharField(max_length=100,null=True, blank=True)
    purchase_bill_number = models.CharField(max_length=255, null=True, blank=True)
    purchase_order_number = models.CharField(max_length=20, null=True, blank=True)
    purchase_order_date = models.DateField(null=True, blank=True)
    purchase_item = models.ManyToManyField(Inventory)
    quantity = models.FloatField(null=True, blank=True, default=1)
    purchase_price = models.FloatField(null=True, blank=True)
    discount = models.FloatField(help_text='in %', null=True, blank=True, default=0)
    unit = models.CharField(max_length=255, choices=(("g","gram"),("kg","kilograms")), default="kg")
    tax = models.FloatField(null=True, blank=True)
    amount = models.FloatField(default=0)
    paid_amount = models.FloatField(default=0)
    balance_amount = models.FloatField(default=0)
    payment_status = models.CharField(max_length=20,choices=PAYMENT_STATUS)
    shipping_cost = models.FloatField(null=True, blank=True)
    received_date = models.DateField(auto_now_add=False, null=True, blank=True)
    purchase_confirmation = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Generate purchase order number if it doesn't exist
        if not self.purchase_bill_number:
            self.purchase_bill_number = self.generate_order_number()

        # Apply discount if available
        discount_factor = 1
        try:
            total_amount = self.amount - float(self.discount)
        except:
            total_amount = self.amount
        
        # Calculate balance amount
        self.balance_amount = total_amount - self.paid_amount

        # Update payment status
        if self.balance_amount <= 0:
            self.payment_status = "PAID"
            self.balance_amount = 0  # Ensure no negative balance
        elif 0 < self.paid_amount < total_amount:
            self.payment_status = "PARTIALLY"
        else:
            self.payment_status = "UNPAID"    
        super().save(*args, **kwargs)

    def generate_order_number(self):
        # Loop to ensure uniqueness
        with transaction.atomic():
        # Get the latest order based on ID to find the last invoice number
            last_order = Purchase.objects.order_by('-id').first()
            
            if last_order and last_order.purchase_bill_number.startswith("PR-"):
                # Extract the numeric part, increment it, and format it with leading zeros
                last_number = int(last_order.purchase_bill_number.split("-")[1])
                new_number = str(last_number + 1).zfill(5)  # Ensures it's 5 digits
            else:
                # Start from "SI-00001" if no previous order exists
                new_number = "00001"
        
        return f"PR-{new_number}"
    def update_totals(self):
        total_amount_before_discount = 0
        total_amount = 0
        total_tax = 0
        total_discount = 0

        for item in self.purchase_bill.all():
            # Calculate the total amount before discount
            item_total_before_discount = item.unit_price * item.quantity
            total_amount_before_discount += item_total_before_discount
            # Sum up the discount for each item
            total_discount += item.discount
            # Calculate the total price (after discount) and total tax for each item
            total_amount += item.total_price  # `total_price` already includes the discount
            

        # self.total_amount_before_discount = total_amount_before_discount
        self.amount = total_amount  # Already discounted total amount
        # self.discount = float(self.discount)  +  float(total_discount)  # Set the order discount as the sum of item discounts
        self.save()

    # def calculate_balance(self):
    #     # Calculate balance amount based on total, discount, and amount paid
    #     discounted_total = self.amount - self.discount
    #     self.balance_amount = discounted_total - self.paid_amount
    #     self.save()


    def __str__(self):
        return f"Purchase {self.id} - {self.supplier}"
    

class PurchaseItems(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='purchase_bill')
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="inventors_purchase")
    quantity = models.FloatField(default=0)
    unit_price = models.FloatField(default=0)
    discount = models.FloatField(default=0)  # Per item discount
    total_price = models.FloatField(editable=False)
    
    def save(self, *args, **kwargs):
        # Calculate total price with discount
        # self.unit_price = 0
        self.total_price = (self.unit_price * self.quantity) - self.discount
        super(PurchaseItems, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.inventory.name} - Quantity: {self.quantity}"







from django.db import models
from django.contrib.auth.models import User

class PaymentTransaction(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cheque', 'Cheque'),
        ('UPI', 'UPI'),
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
    ]
    
    purchase = models.ForeignKey('Purchase', on_delete=models.CASCADE, related_name='payment_transactions')
    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE, related_name='payment_history')
    amount = models.FloatField()
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    reference_number = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment of ₹{self.amount} for {self.purchase.purchase_bill_number} on {self.payment_date}"
    
    class Meta:
        ordering = ['-payment_date', '-created_at']
