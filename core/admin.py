from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget, DateWidget
from .models import *

# Import-Export Resources
class UserRoleResource(resources.ModelResource):
    class Meta:
        model = UserRole
        import_id_fields = ['name']
        fields = ('id', 'name', 'permissions', 'description', 'created_at', 'updated_at')

class UserProfileResource(resources.ModelResource):
    user = Field(attribute='user', column_name='user', widget=ForeignKeyWidget(User, 'username'))
    role = Field(attribute='role', column_name='role', widget=ForeignKeyWidget(UserRole, 'name'))
    
    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'role', 'phone', 'is_active', 'created_at', 'updated_at')

class RegionResource(resources.ModelResource):
    class Meta:
        model = Region
        import_id_fields = ['reg_code']
        fields = ('id', 'region', 'reg_code', 'pilot', 'created_at', 'updated_at')

class DistrictResource(resources.ModelResource):
    region_foreignkey = Field(attribute='region_foreignkey', column_name='region', widget=ForeignKeyWidget(Region, 'reg_code'))
    
    class Meta:
        model = District
        import_id_fields = ['district_code']
        fields = ('id', 'district', 'district_code', 'region', 'reg_code', 'region_foreignkey', 'created_at', 'updated_at')

class DepartmentResource(resources.ModelResource):
    class Meta:
        model = Department
        import_id_fields = ['code']
        fields = ('id', 'name', 'description', 'code', 'is_active', 'created_at', 'updated_at')

class ZoneResource(resources.ModelResource):
    class Meta:
        model = Zone
        import_id_fields = ['code']
        fields = ('id', 'name', 'code', 'zone_type', 'boundary', 'description', 'is_active', 'created_at', 'updated_at')

class PropertyTypeResource(resources.ModelResource):
    class Meta:
        model = PropertyType
        import_id_fields = ['g_code']
        fields = ('id', 'name', 'g_code', 'description', 'base_rate', 'is_active', 'created_at', 'updated_at')

class PropertyResource(resources.ModelResource):
    zone = Field(attribute='zone', column_name='zone', widget=ForeignKeyWidget(Zone, 'code'))
    property_type = Field(attribute='property_type', column_name='property_type', widget=ForeignKeyWidget(PropertyType, 'code'))
    
    class Meta:
        model = Property
        import_id_fields = ['property_id']
        fields = ('id', 'geom', 'g_code', 'area_in_me', 
                 'gpsname', 'region', 'district', 'postcode', 'nlat', 'slat', 'wlong', 
                 'elong', 'area', 'addressv1', 'street', 'latitude', 'longitude', 
                 'created_at', 'updated_at')

class PropertyOwnerResource(resources.ModelResource):
    property = Field(attribute='property', column_name='property', widget=ForeignKeyWidget(Property, 'property_id'))
    
    class Meta:
        model = PropertyOwner
        fields = ('id', 'property', 'owner_name', 'owner_type', 'id_number', 'phone_number', 
                 'email', 'address', 'ownership_percentage', 'is_primary_owner', 
                 'start_date', 'end_date', 'created_at', 'updated_at')

class TaxRateResource(resources.ModelResource):
    zone = Field(attribute='zone', column_name='zone', widget=ForeignKeyWidget(Zone, 'code'))
    property_type = Field(attribute='property_type', column_name='property_type', widget=ForeignKeyWidget(PropertyType, 'code'))
    created_by = Field(attribute='created_by', column_name='created_by', widget=ForeignKeyWidget(User, 'username'))
    
    class Meta:
        model = TaxRate
        fields = ('id', 'zone', 'property_type', 'rate', 'effective_from', 'effective_to', 
                 'description', 'created_by', 'created_at', 'updated_at')

class BillingCycleResource(resources.ModelResource):
    class Meta:
        model = BillingCycle
        fields = ('id', 'name', 'cycle_type', 'start_date', 'end_date', 'due_date', 
                 'is_active', 'created_at', 'updated_at')

class BillResource(resources.ModelResource):
    property = Field(attribute='property', column_name='property', widget=ForeignKeyWidget(Property, 'property_id'))
    billing_cycle = Field(attribute='billing_cycle', column_name='billing_cycle', widget=ForeignKeyWidget(BillingCycle, 'name'))
    created_by = Field(attribute='created_by', column_name='created_by', widget=ForeignKeyWidget(User, 'username'))
    
    class Meta:
        model = Bill
        import_id_fields = ['bill_number']
        fields = ('id', 'bill_number', 'property', 'billing_cycle', 'tax_amount', 
                 'penalty_amount', 'discount_amount', 'total_amount', 'status', 
                 'generated_date', 'due_date', 'sent_date', 'created_by', 'created_at', 'updated_at')

class PaymentResource(resources.ModelResource):
    bill = Field(attribute='bill', column_name='bill', widget=ForeignKeyWidget(Bill, 'bill_number'))
    received_by = Field(attribute='received_by', column_name='received_by', widget=ForeignKeyWidget(User, 'username'))
    
    class Meta:
        model = Payment
        import_id_fields = ['payment_reference']
        fields = ('id', 'payment_reference', 'bill', 'amount', 'payment_method', 
                 'payment_date', 'transaction_id', 'status', 'received_by', 'notes', 
                 'created_at', 'updated_at')

class PenaltyResource(resources.ModelResource):
    property = Field(attribute='property', column_name='property', widget=ForeignKeyWidget(Property, 'property_id'))
    applied_by = Field(attribute='applied_by', column_name='applied_by', widget=ForeignKeyWidget(User, 'username'))
    
    class Meta:
        model = Penalty
        fields = ('id', 'property', 'penalty_type', 'amount', 'reason', 'applied_date', 
                 'due_date', 'is_paid', 'applied_by', 'created_at', 'updated_at')

class ServiceRequestResource(resources.ModelResource):
    property = Field(attribute='property', column_name='property', widget=ForeignKeyWidget(Property, 'property_id'))
    requested_by = Field(attribute='requested_by', column_name='requested_by', widget=ForeignKeyWidget(User, 'username'))
    assigned_to = Field(attribute='assigned_to', column_name='assigned_to', widget=ForeignKeyWidget(User, 'username'))
    
    class Meta:
        model = ServiceRequest
        import_id_fields = ['request_number']
        fields = ('id', 'request_number', 'property', 'request_type', 'description', 
                 'status', 'priority', 'requested_by', 'assigned_to', 'created_at', 
                 'updated_at', 'resolved_at')

class AuditTrailResource(resources.ModelResource):
    user = Field(attribute='user', column_name='user', widget=ForeignKeyWidget(User, 'username'))
    
    class Meta:
        model = AuditTrail
        fields = ('id', 'user', 'action', 'model_name', 'record_id', 'description', 
                 'ip_address', 'timestamp')

class NotificationResource(resources.ModelResource):
    user = Field(attribute='user', column_name='user', widget=ForeignKeyWidget(User, 'username'))
    
    class Meta:
        model = Notification
        fields = ('id', 'user', 'notification_type', 'title', 'message', 'is_read', 
                 'related_object_type', 'related_object_id', 'created_at', 'updated_at')

class ReportResource(resources.ModelResource):
    generated_by = Field(attribute='generated_by', column_name='generated_by', widget=ForeignKeyWidget(User, 'username'))
    
    class Meta:
        model = Report
        fields = ('id', 'name', 'report_type', 'parameters', 'generated_by', 'file_path', 
                 'is_automated', 'schedule', 'created_at', 'updated_at')

class GISDataResource(resources.ModelResource):
    created_by = Field(attribute='created_by', column_name='created_by', widget=ForeignKeyWidget(User, 'username'))
    
    class Meta:
        model = GISData
        fields = ('id', 'name', 'layer_type', 'geo_data', 'style_config', 'is_active', 
                 'created_by', 'created_at', 'updated_at')

class SystemConfigurationResource(resources.ModelResource):
    updated_by = Field(attribute='updated_by', column_name='updated_by', widget=ForeignKeyWidget(User, 'username'))
    
    class Meta:
        model = SystemConfiguration
        import_id_fields = ['key']
        fields = ('id', 'key', 'value', 'data_type', 'description', 'is_public', 
                 'updated_by', 'updated_at')

class RevenueResource(resources.ModelResource):
    payment = Field(attribute='payment', column_name='payment', widget=ForeignKeyWidget(Payment, 'payment_reference'))
    
    class Meta:
        model = Revenue
        fields = ('id', 'payment', 'amount', 'revenue_type', 'period', 'created_at', 'updated_at')

class ExpenseResource(resources.ModelResource):
    approved_by = Field(attribute='approved_by', column_name='approved_by', widget=ForeignKeyWidget(User, 'username'))
    
    class Meta:
        model = Expense
        fields = ('id', 'expense_type', 'amount', 'description', 'expense_date', 
                 'approved_by', 'created_at', 'updated_at')

class BudgetResource(resources.ModelResource):
    department = Field(attribute='department', column_name='department', widget=ForeignKeyWidget(Department, 'code'))
    
    class Meta:
        model = Budget
        fields = ('id', 'fiscal_year', 'department', 'allocated_amount', 'utilized_amount', 
                 'created_at', 'updated_at')

class CustomerAccountResource(resources.ModelResource):
    property_owner = Field(attribute='property_owner', column_name='property_owner', widget=ForeignKeyWidget(PropertyOwner, 'owner_name'))
    
    class Meta:
        model = CustomerAccount
        import_id_fields = ['account_number']
        fields = ('id', 'property_owner', 'account_number', 'balance', 'status', 
                 'created_at', 'updated_at')

class CommunicationResource(resources.ModelResource):
    customer = Field(attribute='customer', column_name='customer', widget=ForeignKeyWidget(PropertyOwner, 'owner_name'))
    sent_by = Field(attribute='sent_by', column_name='sent_by', widget=ForeignKeyWidget(User, 'username'))
    
    class Meta:
        model = Communication
        fields = ('id', 'customer', 'message_type', 'subject', 'content', 'sent_date', 
                 'sent_by', 'created_at', 'updated_at')

class LegalCaseResource(resources.ModelResource):
    property = Field(attribute='property', column_name='property', widget=ForeignKeyWidget(Property, 'property_id'))
    legal_team = Field(attribute='legal_team', column_name='legal_team', widget=ForeignKeyWidget(User, 'username'))
    
    class Meta:
        model = LegalCase
        import_id_fields = ['case_number']
        fields = ('id', 'case_number', 'property', 'case_type', 'description', 'status', 
                 'filed_date', 'resolved_date', 'legal_team', 'created_at', 'updated_at')

class DelinquencyResource(resources.ModelResource):
    property = Field(attribute='property', column_name='property', widget=ForeignKeyWidget(Property, 'property_id'))
    
    class Meta:
        model = Delinquency
        fields = ('id', 'property', 'overdue_amount', 'overdue_days', 'status', 
                 'escalation_level', 'last_action_date', 'next_action_date', 
                 'created_at', 'updated_at')

class MobilePaymentProviderResource(resources.ModelResource):
    class Meta:
        model = MobilePaymentProvider
        import_id_fields = ['code']
        fields = ('id', 'name', 'code', 'is_active', 'config', 'created_at', 'updated_at')

class MobilePaymentResource(resources.ModelResource):
    payment = Field(attribute='payment', column_name='payment', widget=ForeignKeyWidget(Payment, 'payment_reference'))
    provider = Field(attribute='provider', column_name='provider', widget=ForeignKeyWidget(MobilePaymentProvider, 'code'))
    
    class Meta:
        model = MobilePayment
        fields = ('id', 'payment', 'provider', 'mobile_number', 'transaction_reference', 
                 'provider_reference', 'created_at', 'updated_at')

class VersionTblResource(resources.ModelResource):
    class Meta:
        model = versionTbl
        fields = ('id', 'version', 'created_at', 'updated_at')

# Admin Classes
@admin.register(UserRole)
class UserRoleAdmin(ImportExportModelAdmin):
    resource_class = UserRoleResource
    list_display = ('name', 'description', 'created_at', 'updated_at')
    list_filter = ('name', 'created_at')
    search_fields = ('name', 'description')

@admin.register(UserProfile)
class UserProfileAdmin(ImportExportModelAdmin):
    resource_class = UserProfileResource
    list_display = ('user', 'role', 'phone', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('user__username', 'phone')

@admin.register(Region)
class RegionAdmin(ImportExportModelAdmin):
    resource_class = RegionResource
    list_display = ('region', 'reg_code', 'pilot', 'created_at')
    list_filter = ('pilot', 'created_at')
    search_fields = ('region', 'reg_code')

@admin.register(District)
class DistrictAdmin(ImportExportModelAdmin):
    resource_class = DistrictResource
    list_display = ('district', 'district_code', 'region', 'reg_code', 'created_at')
    list_filter = ('region', 'created_at')
    search_fields = ('district', 'district_code', 'region')

@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin):
    resource_class = DepartmentResource
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')

@admin.register(Zone)
class ZoneAdmin(ImportExportModelAdmin):
    resource_class = ZoneResource
    list_display = ('name', 'code', 'zone_type', 'is_active', 'created_at')
    list_filter = ('zone_type', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'description')

@admin.register(PropertyType)
class PropertyTypeAdmin(ImportExportModelAdmin):
    resource_class = PropertyTypeResource
    list_display = ('name', 'code', 'base_rate', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')

@admin.register(Property)
class PropertyAdmin(ImportExportModelAdmin):
    resource_class = PropertyResource
    list_display = ('id', 'address', 'g_code', 'area_in_me', 
                 'gpsname', 'region', 'district', 'postcode', 'nlat', 'slat', 'wlong', 
                 'elong', 'area', 'addressv1', 'street', 'latitude', 'longitude', 
                 'created_at', 'updated_at')
    
    list_filter = ('zone', 'property_type', 'created_at')
    search_fields = ( 'address', 'region', 'district')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PropertyOwner)
class PropertyOwnerAdmin(ImportExportModelAdmin):
    resource_class = PropertyOwnerResource
    list_display = ('owner_name', 'property', 'owner_type', 'is_primary_owner', 'start_date', 'created_at')
    list_filter = ('owner_type', 'is_primary_owner', 'start_date', 'created_at')
    search_fields = ('owner_name', 'property__property_id', 'id_number')

@admin.register(TaxRate)
class TaxRateAdmin(ImportExportModelAdmin):
    resource_class = TaxRateResource
    list_display = ('zone', 'property_type', 'rate', 'effective_from', 'effective_to', 'created_by', 'created_at')
    list_filter = ('zone', 'property_type', 'effective_from', 'created_at')
    search_fields = ('zone__name', 'property_type__name')

@admin.register(BillingCycle)
class BillingCycleAdmin(ImportExportModelAdmin):
    resource_class = BillingCycleResource
    list_display = ('name', 'cycle_type', 'start_date', 'end_date', 'due_date', 'is_active', 'created_at')
    list_filter = ('cycle_type', 'is_active', 'start_date', 'created_at')
    search_fields = ('name',)

@admin.register(Bill)
class BillAdmin(ImportExportModelAdmin):
    resource_class = BillResource
    list_display = ('bill_number', 'property', 'billing_cycle', 'total_amount', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'billing_cycle', 'due_date', 'created_at')
    search_fields = ('bill_number', 'property__property_id')

@admin.register(Payment)
class PaymentAdmin(ImportExportModelAdmin):
    resource_class = PaymentResource
    list_display = ('payment_reference', 'bill', 'amount', 'payment_method', 'status', 'payment_date', 'created_at')
    list_filter = ('payment_method', 'status', 'payment_date', 'created_at')
    search_fields = ('payment_reference', 'bill__bill_number', 'transaction_id')

@admin.register(Penalty)
class PenaltyAdmin(ImportExportModelAdmin):
    resource_class = PenaltyResource
    list_display = ('property', 'penalty_type', 'amount', 'applied_date', 'due_date', 'is_paid', 'created_at')
    list_filter = ('penalty_type', 'is_paid', 'applied_date', 'created_at')
    search_fields = ('property__property_id', 'reason')

@admin.register(ServiceRequest)
class ServiceRequestAdmin(ImportExportModelAdmin):
    resource_class = ServiceRequestResource
    list_display = ('request_number', 'property', 'request_type', 'status', 'priority', 'requested_by', 'created_at')
    list_filter = ('request_type', 'status', 'priority', 'created_at')
    search_fields = ('request_number', 'property__property_id', 'description')

@admin.register(AuditTrail)
class AuditTrailAdmin(ImportExportModelAdmin):
    resource_class = AuditTrailResource
    list_display = ('user', 'action', 'model_name', 'record_id', 'timestamp', 'ip_address')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'model_name', 'record_id')
    readonly_fields = ('timestamp',)

@admin.register(Notification)
class NotificationAdmin(ImportExportModelAdmin):
    resource_class = NotificationResource
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')

@admin.register(Report)
class ReportAdmin(ImportExportModelAdmin):
    resource_class = ReportResource
    list_display = ('name', 'report_type', 'generated_by', 'is_automated', 'created_at')
    list_filter = ('report_type', 'is_automated', 'created_at')
    search_fields = ('name', 'report_type')

@admin.register(GISData)
class GISDataAdmin(ImportExportModelAdmin):
    resource_class = GISDataResource
    list_display = ('name', 'layer_type', 'is_active', 'created_by', 'created_at')
    list_filter = ('layer_type', 'is_active', 'created_at')
    search_fields = ('name', 'layer_type')

@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(ImportExportModelAdmin):
    resource_class = SystemConfigurationResource
    list_display = ('key', 'value', 'data_type', 'is_public', 'updated_by', 'updated_at')
    list_filter = ('data_type', 'is_public', 'updated_at')
    search_fields = ('key', 'description')
    readonly_fields = ('updated_at',)

@admin.register(Revenue)
class RevenueAdmin(ImportExportModelAdmin):
    resource_class = RevenueResource
    list_display = ('payment', 'amount', 'revenue_type', 'period', 'created_at')
    list_filter = ('revenue_type', 'period', 'created_at')
    search_fields = ('payment__payment_reference', 'revenue_type')

@admin.register(Expense)
class ExpenseAdmin(ImportExportModelAdmin):
    resource_class = ExpenseResource
    list_display = ('expense_type', 'amount', 'expense_date', 'approved_by', 'created_at')
    list_filter = ('expense_type', 'expense_date', 'created_at')
    search_fields = ('expense_type', 'description')

@admin.register(Budget)
class BudgetAdmin(ImportExportModelAdmin):
    resource_class = BudgetResource
    list_display = ('fiscal_year', 'department', 'allocated_amount', 'utilized_amount', 'created_at')
    list_filter = ('fiscal_year', 'department', 'created_at')
    search_fields = ('fiscal_year', 'department__name')

@admin.register(CustomerAccount)
class CustomerAccountAdmin(ImportExportModelAdmin):
    resource_class = CustomerAccountResource
    list_display = ('account_number', 'property_owner', 'balance', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('account_number', 'property_owner__owner_name')

@admin.register(Communication)
class CommunicationAdmin(ImportExportModelAdmin):
    resource_class = CommunicationResource
    list_display = ('customer', 'message_type', 'subject', 'sent_date', 'sent_by', 'created_at')
    list_filter = ('message_type', 'sent_date', 'created_at')
    search_fields = ('customer__owner_name', 'subject', 'content')

@admin.register(LegalCase)
class LegalCaseAdmin(ImportExportModelAdmin):
    resource_class = LegalCaseResource
    list_display = ('case_number', 'property', 'case_type', 'status', 'filed_date', 'legal_team', 'created_at')
    list_filter = ('case_type', 'status', 'filed_date', 'created_at')
    search_fields = ('case_number', 'property__property_id', 'case_type')

@admin.register(Delinquency)
class DelinquencyAdmin(ImportExportModelAdmin):
    resource_class = DelinquencyResource
    list_display = ('property', 'overdue_amount', 'overdue_days', 'status', 'escalation_level', 'last_action_date', 'created_at')
    list_filter = ('status', 'escalation_level', 'last_action_date', 'created_at')
    search_fields = ('property__property_id',)

@admin.register(MobilePaymentProvider)
class MobilePaymentProviderAdmin(ImportExportModelAdmin):
    resource_class = MobilePaymentProviderResource
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')

@admin.register(MobilePayment)
class MobilePaymentAdmin(ImportExportModelAdmin):
    resource_class = MobilePaymentResource
    list_display = ('payment', 'provider', 'mobile_number', 'transaction_reference', 'created_at')
    list_filter = ('provider', 'created_at')
    search_fields = ('payment__payment_reference', 'mobile_number', 'transaction_reference')

@admin.register(versionTbl)
class VersionTblAdmin(ImportExportModelAdmin):
    resource_class = VersionTblResource
    list_display = ('version', 'created_at', 'updated_at')
    list_filter = ('created_at',)