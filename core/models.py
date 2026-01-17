import random
import secrets
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal



from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from datetime import date
import uuid
from django.contrib.gis.db.models import GeometryField
from django.contrib.auth import get_user_model


User = get_user_model()




# Custom managers for soft delete functionality
class TimeStampManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(TimeStampManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return TimeStampQuerySet(self.model).filter(is_deleted=False)
        return TimeStampQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()

class TimeStampQuerySet(models.QuerySet):
    def delete(self):
        return self.update(is_deleted=True)
    
    def hard_delete(self):
        return super(TimeStampQuerySet, self).delete()
    
    def alive(self):
        return self.filter(is_deleted=False)
    
    def dead(self):
        return self.filter(is_deleted=True)

class TimeStampModel(models.Model):
    """
    Abstract base model with timestamp and soft delete functionality
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_created')
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_modified')
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_deleted')
    
    objects = TimeStampManager()
    all_objects = models.Manager()
    
    class Meta:
        abstract = True
    
    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
    
    def hard_delete(self, *args, **kwargs):
        super(TimeStampModel, self).delete(*args, **kwargs)



class versionTbl(TimeStampModel):
 version = models.IntegerField(blank=True, null=True)


# Missing: User roles, departments, permissions
class UserRole(TimeStampModel):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('ceo', 'CEO'),
        ('director', 'Director'),
        ('finance_team', 'Finance Team'),
        ('assessment_team', 'Assessment Team'),
        
    )
    name = models.CharField(max_length=50, choices=ROLE_CHOICES)
    permissions = models.JSONField()  # Store specific permissions
    description = models.TextField(blank=True)

class UserProfile(TimeStampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(UserRole, on_delete=models.PROTECT)
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)

# Region and District Models
class Region(TimeStampModel):
    region = models.CharField(max_length=250, unique=True)
    reg_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    pilot = models.BooleanField(default=False) 
    geom = GeometryField(blank=True, null=True, srid=4326)
    
    def __str__(self):
        return self.region
    
    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"

class District(TimeStampModel):
    district = models.CharField(max_length=250)
    district_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    region = models.CharField(max_length=250, null=True, blank=True)
    reg_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    region_foreignkey = models.ForeignKey(
        'Region',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='districts',
        to_field='reg_code'  # This is the key change
    )
    geom = GeometryField(blank=True, null=True, srid=4326)
    
    def __str__(self):
        return f"{self.district} ({self.region})"
    
    def save(self, *args, **kwargs):
        # Auto-populate the region_foreignkey based on the reg_code
        if self.reg_code and not self.region_foreignkey:
            try:
                region_obj = Region.objects.get(reg_code=self.reg_code)
                self.region_foreignkey = region_obj
            except Region.DoesNotExist:
                pass
        super().save(*args, **kwargs)


class Department(TimeStampModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name

class Zone(TimeStampModel):
    ZONE_TYPE_CHOICES = (
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('agricultural', 'Agricultural'),
        ('mixed_use', 'Mixed Use'),
    )
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPE_CHOICES)
    boundary = models.JSONField()  # GeoJSON for zone boundaries
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.zone_type})"


class PropertyType(TimeStampModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Property(TimeStampModel):
    PROPERTY_STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('under_construction', 'Under Construction'),
        ('demolished', 'Demolished'),
    )
    
    # property_id = models.CharField(max_length=20, unique=True)
    address = models.TextField(null=True, blank=True)
    coordinates = models.JSONField(null=True, blank=True)  # Latitude and longitude
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name='properties')
    property_type = models.ForeignKey(PropertyType, on_delete=models.PROTECT, related_name='properties')
    geom = GeometryField(blank=True, null=True, srid=4326)
    g_code = models.CharField(max_length=50, blank=True)  # Geographic code
    area_in_me = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Area in Square Meters")  # Alternative area field
    gpsname = models.CharField(max_length=200, blank=True, verbose_name="GPS Name")  # GPS location name
    region = models.CharField(max_length=100, blank=True)  # Region name
    district = models.CharField(max_length=100, blank=True)  # District name
    postcode = models.CharField(max_length=20, blank=True, verbose_name="Postal Code")  # Postal code
    nlat = models.DecimalField(max_digits=15, decimal_places=12, null=True, blank=True, verbose_name="Northern Latitude")  # Northern boundary latitude
    slat = models.DecimalField(max_digits=15, decimal_places=12, null=True, blank=True, verbose_name="Southern Latitude")  # Southern boundary latitude
    wlong = models.DecimalField(max_digits=15, decimal_places=12, null=True, blank=True, verbose_name="Western Longitude")  # Western boundary longitude
    elong = models.DecimalField(max_digits=15, decimal_places=12, null=True, blank=True, verbose_name="Eastern Longitude")  # Eastern boundary longitude
    area = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Area")  # Alternative area measurement
    addressv1 = models.TextField(blank=True, verbose_name="Address Version 1")  # Alternative address format
    street = models.CharField(max_length=200, blank=True)  # Street name
    latitude = models.DecimalField(max_digits=15, decimal_places=12, null=True, blank=True)  # Point latitude
    longitude = models.DecimalField(max_digits=15, decimal_places=12, null=True, blank=True)  # Point longitude


    # def generate_property_id(self):
    #     # Generate a random property ID
    #     property_id = secrets.token_hex(10)
    #     return property_id
  

    def __str__(self):
        return f"{self.address}"


class PropertyOwner(TimeStampModel):
    OWNER_TYPE_CHOICES = (
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('government', 'Government'),
        ('trust', 'Trust'),
    )
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='owners')
    owner_name = models.CharField(max_length=200)
    owner_type = models.CharField(max_length=20, choices=OWNER_TYPE_CHOICES)
    id_number = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    ownership_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    is_primary_owner = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.owner_name} - {self.property.property_id}"

class TaxRate(TimeStampModel):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='tax_rates')
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE, related_name='tax_rates')
    rate = models.DecimalField(max_digits=6, decimal_places=4)  # Tax rate as percentage
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='tax_rates_created')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.zone.name} - {self.property_type.name}: {self.rate}%"

class BillingCycle(TimeStampModel):
    CYCLE_TYPE_CHOICES = (
        ('annual', 'Annual'),
        ('semi_annual', 'Semi-Annual'),
        ('quarterly', 'Quarterly'),
        ('monthly', 'Monthly'),
    )
    
    name = models.CharField(max_length=100)
    cycle_type = models.CharField(max_length=20, choices=CYCLE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    due_date = models.DateField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"

class Bill(TimeStampModel):
    BILL_STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )
    
    bill_number = models.CharField(max_length=100, unique=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bills')
    billing_cycle = models.ForeignKey(BillingCycle, on_delete=models.PROTECT, related_name='bills', null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=100, choices=BILL_STATUS_CHOICES, default='draft')
    generated_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    sent_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bills_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill {self.bill_number} - {self.property.property_id}"

class Payment(TimeStampModel):
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('cheque', 'Cheque'),
        ('online', 'Online Payment'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    payment_reference = models.CharField(max_length=50, unique=True)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField()
    transaction_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    received_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='payments_received')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Payment {self.payment_reference} - {self.amount}"

class Penalty(TimeStampModel):
    PENALTY_TYPE_CHOICES = (
        ('late_payment', 'Late Payment'),
        ('under_assessment', 'Under Assessment'),
        ('non_compliance', 'Non-Compliance'),
    )
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='penalties')
    penalty_type = models.CharField(max_length=20, choices=PENALTY_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    applied_date = models.DateField()
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    applied_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='penalties_applied')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Penalty - {self.property.property_id} - {self.penalty_type}"

class ServiceRequest(TimeStampModel):
    REQUEST_TYPE_CHOICES = (
        ('valuation_review', 'Valuation Review'),
        ('ownership_transfer', 'Ownership Transfer'),
        ('payment_issue', 'Payment Issue'),
        ('information_request', 'Information Request'),
        ('complaint', 'Complaint'),
    )
    
    REQUEST_STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    request_number = models.CharField(max_length=20, unique=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='service_requests')
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPE_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    requested_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='requests_made')
    assigned_to = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='requests_assigned')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'service_requests'

    def __str__(self):
        return f"SR-{self.request_number} - {self.request_type}"

class AuditTrail(TimeStampModel):
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    )
    
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='audit_trails')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    record_id = models.CharField(max_length=50)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_trails'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['model_name', 'record_id']),
        ]

    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.action} - {self.model_name}"

class Notification(TimeStampModel):
    NOTIFICATION_TYPE_CHOICES = (
        ('bill_generated', 'Bill Generated'),
        ('payment_received', 'Payment Received'),
        ('payment_overdue', 'Payment Overdue'),
        ('service_request', 'Service Request'),
        ('system_alert', 'System Alert'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class Report(TimeStampModel):
    REPORT_TYPE_CHOICES = (
        ('revenue_summary', 'Revenue Summary'),
        ('collection_performance', 'Collection Performance'),
        ('property_inventory', 'Property Inventory'),
        ('delinquency_report', 'Delinquency Report'),
        ('zone_analysis', 'Zone Analysis'),
        ('custom', 'Custom Report'),
    )
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    parameters = models.JSONField()  # Store report filters and parameters
    generated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reports_generated')
    file_path = models.FileField(upload_to='reports/', null=True, blank=True)
    is_automated = models.BooleanField(default=False)
    schedule = models.CharField(max_length=50, blank=True)  # For automated reports
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reports'

    def __str__(self):
        return self.name

class GISData(TimeStampModel):
    LAYER_TYPE_CHOICES = (
        ('property_boundaries', 'Property Boundaries'),
        ('zones', 'Zones'),
        ('revenue_heatmap', 'Revenue Heatmap'),
        ('collection_density', 'Collection Density'),
        ('infrastructure', 'Infrastructure'),
    )
    
    name = models.CharField(max_length=200)
    layer_type = models.CharField(max_length=30, choices=LAYER_TYPE_CHOICES)
    geo_data = models.JSONField()  # GeoJSON data
    style_config = models.JSONField()  # Styling configuration for the layer
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='gis_data_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gis_data'

    def __str__(self):
        return f"{self.name} ({self.layer_type})"

class SystemConfiguration(TimeStampModel):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    data_type = models.CharField(max_length=20, choices=[
        ('string', 'String'),
        ('integer', 'Integer'),
        ('decimal', 'Decimal'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ])
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='system_configurations_updated')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system_configurations'

    def __str__(self):
        return self.key



# Missing: Revenue tracking, expenses, budget
class Revenue(TimeStampModel):
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    revenue_type = models.CharField(max_length=50)  # tax, penalty, etc.
    period = models.DateField()  # Monthly revenue period

class Expense(TimeStampModel):
    expense_type = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    expense_date = models.DateField()
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT)

class Budget(TimeStampModel):
    fiscal_year = models.CharField(max_length=10)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2)
    utilized_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)




# Missing: Customer accounts, communications
class CustomerAccount(TimeStampModel):
    property_owner = models.ForeignKey(PropertyOwner, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')])

class Communication(TimeStampModel):
    MESSAGE_TYPE_CHOICES = (
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('notification', 'Notification'),
        ('letter', 'Letter'),
    )
    customer = models.ForeignKey(PropertyOwner, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    sent_date = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey(User, on_delete=models.PROTECT)



# Missing: Legal case management
class LegalCase(TimeStampModel):
    CASE_STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_court', 'In Court'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    case_number = models.CharField(max_length=20, unique=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    case_type = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=CASE_STATUS_CHOICES)
    filed_date = models.DateField()
    resolved_date = models.DateField(null=True, blank=True)
    legal_team = models.ForeignKey(User, on_delete=models.PROTECT, related_name='legal_cases')


# Missing: Delinquency tracking
class Delinquency(TimeStampModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    overdue_amount = models.DecimalField(max_digits=12, decimal_places=2)
    overdue_days = models.IntegerField()
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('resolved', 'Resolved')])
    escalation_level = models.IntegerField(default=1)  # 1, 2, 3 for different actions
    last_action_date = models.DateField()
    next_action_date = models.DateField()


# Missing: Mobile payment providers
class MobilePaymentProvider(TimeStampModel):
    name = models.CharField(max_length=100)  # MTN, Vodafone, AirtelTigo, etc.
    code = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    config = models.JSONField()  # API keys, endpoints, etc.

class MobilePayment(TimeStampModel):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    provider = models.ForeignKey(MobilePaymentProvider, on_delete=models.PROTECT)
    mobile_number = models.CharField(max_length=15)
    transaction_reference = models.CharField(max_length=100)
    provider_reference = models.CharField(max_length=100, blank=True)